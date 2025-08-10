"""
Optimizador automático de assets web
Archivo: optimizador_assets_web.py

Descripción
-----------
Script CLI en Python que analiza un directorio de assets (imágenes y videos),
crea versiones optimizadas (WebP, AVIF si está disponible), genera tamaños
responsive, produce snippets HTML sugeridos (srcset + lazy-loading) y un
informe JSON con los ahorros en bytes.

Requisitos
----------
- Python 3.8+
- ffmpeg instalado y accesible en PATH (recomendado para conversión AVIF/webp y videos)
- Pillow (pip install pillow) — usado como fallback para WebP si ffmpeg no está

Limitaciones
-----------
- AVIF conversion depende de ffmpeg compilado con soporte libaom/libdav1d.
- Este script intenta usar ffmpeg si está disponible; si no, usa Pillow para WebP (sin AVIF).

Uso básico
---------
python optimizador_assets_web.py --input ./static --output ./static_optimized --formats webp,avif --sizes 320,640,1280 --report report.json

Salida
-----
- Directorio de salida con la misma estructura que la entrada y assets optimizados.
- report.json con metadatos y ahorro por archivo.
- snippets.html con ejemplos de <img> y <video> optimizados y srcset.

"""

from __future__ import annotations
import time
import argparse
import os
import shutil
import subprocess
import sys
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

# Importamos la instancia de Image (imagen) de Pillow (PIL)
try:
    from PIL import Image 
except Exception:
    Image = None 

# Barra de carga opcional (tqdm). Si no está instalado, el script sigue funcionando y usa prints simples.
try:
    from tqdm import tqdm
except Exception:
    tqdm = None

try:
    import psutil
except ImportError:
    psutil = None

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'}

@dataclass
class VarianteOptimizada: # Inicializamos la clase de la variante del archivo optimizada, para tipado.
    path: str
    format: str
    width: Optional[int]
    size: int

@dataclass
class ReporteAssets: # Inicializamos la clase que se usará para el reporte final de conversión.
    original_path: str
    original_size: int
    variants: List[VarianteOptimizada]


def encontrar_assets(root: Path) -> Tuple[List[Path], List[Path]]: # Definimos la función que rastrea y almacena las direcciones de los assets que queremos convertir
    imagenes = []
    videos = []
    for p in root.rglob('*'):
        if p.is_file():
            ext = p.suffix.lower()
            if ext in IMAGE_EXTS:
                imagenes.append(p)
            elif ext in VIDEO_EXTS:
                videos.append(p)
    return imagenes, videos


def human(n: int) -> str: # Definimos la función para almacenar el tamaño del archivo con su unidad.
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(n) < 1024.0:
            return f"{n:3.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}PB"

def terminar_peh(pid: int): # Definimos la función para terminar los procesos y sus hijos en caso de requerirlo
    if psutil is None:
        return False
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
        return True
    except Exception:
        return False


def asegurar_dir(p: Path): # Definimos la función para guardar el directorio del archivo
    p.parent.mkdir(parents=True, exist_ok=True)


def ffmpeg_disponible() -> bool: # Definimos la función que nos indica si ffmpeg está disponible en el entorno
    return shutil.which('ffmpeg') is not None


def conv_im_c_ffmpeg(src: Path, dest: Path, width: Optional[int], fmt: str) -> bool: # Definimos la función para convertir imagenes con FFMPEG
    # Escalado de ffmpeg: Mantiene la relación de aspecto (-1 de altura)
    cmd = ['ffmpeg', '-y', '-i', str(src)]
    vf = []
    if width:
        vf.append(f"scale='min({width},iw)':'-2'")  # Mantiene la altura de la imagen
    if vf:
        cmd += ['-vf', ','.join(vf)]
    # Escoje el encoder/parametros de conversión
    if fmt == 'webp':
        cmd += ['-c:v', 'libwebp', '-lossless', '0', '-q:v', '80']
    elif fmt == 'avif':
        cmd += ['-c:v', 'libaom-av1', '-crf', '30', '-b:v', '0']
    else:
        # fallback de encoding por la extensión del archivo si el formato no es valido
        pass
    cmd.append(str(dest))
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def conv_im_c_pillow(src: Path, dest: Path, width: Optional[int], fmt: str) -> bool: # Definimos la función para conversión de Pillow, si es que no poseemos ffmpeg
    if Image is None:
        return False
    try:
        with Image.open(src) as im:
            # convertir PNG/GIF a RGB para formatos web
            if im.mode in ('P', 'RGBA') and fmt.lower() in ('jpeg', 'jpg'):
                im = im.convert('RGB')
            if width and im.width > width:
                # mantiene la relación de aspecto
                height = round((width / im.width) * im.height)
                im = im.resize((width, height), Image.LANCZOS)
            asegurar_dir(dest)
            params = {}
            if fmt.lower() == 'webp':
                params['quality'] = 80
            im.save(dest, format=fmt.upper(), **params)
        return True
    except Exception:
        return False


def crear_output_path(input_root: Path, output_root: Path, src: Path, suffix: str, ext: str) -> Path: # Definimos la función que crea el directorio de salida de
    rel = src.relative_to(input_root)
    out = output_root / rel.parent / (rel.stem + suffix + ext)
    return out


def gen_var_im(input_root: Path, output_root: Path, src: Path, formats: List[str], sizes: List[int], use_ffmpeg: bool, keep_larger: bool = False) -> ReporteAssets: # Definimos la función de las variantes de imagenes
    orig_size = src.stat().st_size
    variants: List[VarianteOptimizada] = []
    widths = sorted(set([None] + sizes), key=lambda x: (x is None, x if x is not None else float('inf')))  # Pone 'None' mientras ve tamaños  # Incluye el tamaño original (None -> full)

    for w in widths:
        for fmt in formats:
            ext = f'.{fmt.lower()}'
            suffix = f'.w{w}' if w else ''
            out = crear_output_path(input_root, output_root, src, suffix, ext)
            asegurar_dir(out)
            success = False
            if use_ffmpeg:
                success = conv_im_c_ffmpeg(src, out, w, fmt)
            if not success:
                # Prueba el fallback de pillow para webp
                if fmt.lower() == 'webp' and Image is not None:
                    success = conv_im_c_pillow(src, out, w, fmt)
            if success and out.exists():
                vsize = out.stat().st_size
                # Solo mantiene las variantes que son mas pequeñas que el archivo original
                if not keep_larger and vsize >= orig_size:
                    try:
                        out.unlink()
                    except Exception:
                        pass
                else:
                    variants.append(VarianteOptimizada(path=str(out), format=fmt, width=w, size=vsize))
    return ReporteAssets(original_path=str(src), original_size=orig_size, variants=variants)



def conv_vid_c_ffmpeg(src: Path, dest: Path, preset: str, target_crf: int = None, timeout: int = 60) -> bool:
    ext = dest.suffix.lower()
    cmd = ['ffmpeg', '-y', '-i', str(src)]

    # Selección de codec y parámetros según formato
    if ext == '.mp4':
        cmd += ['-c:v', 'libx264']
        if target_crf is not None:
            cmd += ['-crf', str(target_crf)]
        else:
            cmd += ['-crf', '23']
        cmd += ['-preset', preset, '-c:a', 'aac', '-b:a', '128k']

    elif ext == '.webm':
        cmd += ['-c:v', 'libvpx-vp9']
        if target_crf is not None:
            cmd += ['-crf', str(target_crf)]
        else:
            cmd += ['-crf', '30']
        cmd += ['-b:v', '0', '-c:a', 'libopus']

    else:
        cmd += ['-c:v', 'libx264', '-crf', str(target_crf or 23), '-preset', preset]

    cmd.append(str(dest))

    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"⚠️ Conversión de {src} cancelada por exceder {timeout} segundos. Intentando detener proceso...")

        # Intentar terminar proceso y sus hijos
        if psutil:
            killed = terminar_peh(process.pid)
            if not killed:
                process.terminate()
                time.sleep(3)
                if process.poll() is None:
                    process.kill()
        else:
            process.terminate()
            time.sleep(3)
            if process.poll() is None:
                process.kill()

        process.communicate()  # Liberar recursos

        if dest.exists():
            try:
                dest.unlink()
            except Exception as e:
                print(f"⚠️ No se pudo borrar archivo parcial {dest}: {e}")
        return False

    if process.returncode == 0 and dest.exists():
        return True
    else:
        if dest.exists():
            try:
                dest.unlink()
            except Exception:
                pass
        return False


def generar_vid_var(input_root: Path, output_root: Path, src: Path, presets: List[Tuple[str, str]], keep_larger: bool = False) -> "ReporteAssets":
    orig_size = src.stat().st_size
    variants: List["VarianteOptimizada"] = []
    generated_files: List[Path] = []
    mp4_variant: Optional[Path] = None

    for suffix, ext in presets:
        out = crear_output_path(input_root, output_root, src, suffix, ext)
        asegurar_dir(out)

        if not ffmpeg_disponible():
            continue

        crf = 28  # valor inicial
        max_crf = 35

        while crf <= max_crf:
            temp_out = out.with_name(f"{out.stem}_crf{crf}{ext}")
            success = conv_vid_c_ffmpeg(src, temp_out, 'medium', target_crf=crf, timeout=120)

            if not success or not temp_out.exists():
                # Si es .webm y falló, pero hay un mp4 generado, borra todo menos el mp4
                if ext == '.webm' and mp4_variant and mp4_variant.exists():
                    for f in generated_files:
                        if f != mp4_variant and f.exists():
                            try:
                                f.unlink()
                            except Exception:
                                pass
                    variants = [v for v in variants if v.format == 'mp4']
                    generated_files = [mp4_variant]
                break

            vsize = temp_out.stat().st_size

            if not keep_larger and vsize >= orig_size:
                try:
                    temp_out.unlink()
                except Exception:
                    pass
            else:
                try:
                    temp_out.rename(out)
                except Exception:
                    pass
                variants.append(
                    VarianteOptimizada(path=str(out), format=ext.lstrip('.'), width=None, size=out.stat().st_size)
                )
                generated_files.append(out)
                if ext == '.mp4':
                    mp4_variant = out

                # Si la variante generada es .webm, eliminar todas las demás variantes generadas
                if ext == '.webm':
                    for f in generated_files:
                        if f != out and f.exists():
                            try:
                                f.unlink()
                            except Exception:
                                pass
                    variants = [v for v in variants if v.format == 'webm']
                    generated_files = [out]
                    break

            crf += 2  # aumentar compresión

    # Al finalizar, limpiar variantes intermedias y dejar solo la mejor
    # Si hay .webm, solo queda .webm; si no, solo queda el mejor .mp4
    if any(v.format == 'webm' for v in variants):
        final_format = 'webm'
    elif any(v.format == 'mp4' for v in variants):
        final_format = 'mp4'
    else:
        final_format = None

    # Filtra variantes para dejar solo la final en el reporte
    variants = [v for v in variants if v.format == final_format]

    return ReporteAssets(original_path=str(src), original_size=orig_size, variants=variants)


def procesar_assets(input_dir: Path, output_dir: Path, formats: List[str], sizes: List[int], video_presets: List[Tuple[str, str]], workers: int, dry_run: bool, keep_larger: bool) -> Dict:
    images, videos = encontrar_assets(input_dir)
    total_jobs = len(images) + len(videos)
    print(f"Found {len(images)} images and {len(videos)} videos (total jobs: {total_jobs})")
    use_ffmpeg = ffmpeg_disponible()
    print(f"ffmpeg available: {use_ffmpeg}; Pillow available: {Image is not None}")

    reports: List[ReporteAssets] = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = []
        for img in images:
            future = ex.submit(gen_var_im, input_dir, output_dir, img, formats, sizes, use_ffmpeg, keep_larger)
            futures.append(future)
        for vid in videos:
            future = ex.submit(generar_vid_var, input_dir, output_dir, vid, video_presets, keep_larger)
            futures.append(future)

        # Mostrar barra de progreso usando tqdm si está disponible; si no, mostramos un contador simple
        processed = 0
        if tqdm is not None:
            for fut in tqdm(as_completed(futures), total=len(futures), desc="Processing assets"):
                try:
                    rep = fut.result()
                    reports.append(rep)
                except Exception as e:
                    print("Error processing asset:", e)
        else:
            for fut in as_completed(futures):
                try:
                    rep = fut.result()
                    reports.append(rep)
                except Exception as e:
                    print("Error processing asset:", e)
                processed += 1
                print(f"Processed {processed}/{len(futures)}")

    # build aggregated report
    total_original = sum(r.original_size for r in reports)
    total_final = sum(sum(v.size for v in r.variants) for r in reports)
    total_saved = total_original - total_final
    summary = {
        'input_dir': str(input_dir),
        'output_dir': str(output_dir),
        'num_assets': len(reports),
        'total_original_bytes': total_original,
        'total_final_bytes': total_final,
        'total_saved_bytes': total_saved,
        'percent_reduction': (total_saved / total_original * 100) if total_original else 0,
        'assets': [asdict(r) for r in reports]
    }
    return summary


def guardar_reporte(report: Dict, path: Path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def generate_html_snippets(report: Dict, out_path: Path):
    lines = ['<!doctype html>', '<html><head><meta charset="utf-8"><title>Snippets</title></head><body>']
    for r in report.get('assets', []):
        orig = r['original_path']
        variants = r['variants']
        img_variants = [v for v in variants if v['format'].lower() not in ['mp4', 'webm', 'mov', 'avi']]
        vid_variants = [v for v in variants if v['format'].lower() in ['mp4', 'webm']]
        if img_variants:
            by_format: Dict[str, List[Dict]] = {}
            for v in img_variants:
                by_format.setdefault(v['format'].lower(), []).append(v)
            preferred = 'webp' if 'webp' in by_format else list(by_format.keys())[0]
            srcset_items = []
            for v in sorted(by_format.get(preferred, []), key=lambda x: (x['width'] or 9999)):
                width = v['width']
                if width:
                    srcset_items.append(f"{os.path.relpath(v['path'])} {width}w")
                else:
                    srcset_items.append(f"{os.path.relpath(v['path'])} 1x")
            srcset = ', '.join(srcset_items)
            lines.append('<picture>')
            for fmt, items in by_format.items():
                src = os.path.relpath(items[-1]['path'])
                lines.append(f"  <source type=\"image/{fmt}\" srcset=\"{srcset}\">")
            fallback = os.path.relpath(img_variants[0]['path'])
            lines.append(f"  <img src=\"{fallback}\" srcset=\"{srcset}\" loading=\"lazy\" alt=\"Optimized image\">")
            lines.append('</picture>')
        if vid_variants:
            lines.append('<video controls muted preload="metadata">')
            for v in vid_variants:
                rel = os.path.relpath(v['path'])
                mime = 'video/mp4' if v['format'].lower() == 'mp4' else 'video/webm'
                lines.append(f"  <source src=\"{rel}\" type=\"{mime}\">")
            lines.append('  Tu navegador no soporta el tag.')
            lines.append('</video>')
        lines.append('<hr>')
    lines.append('</body></html>')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def parse_args():
    p = argparse.ArgumentParser(description='Optimizador automático de assets web')
    p.add_argument('--input', '--input-dir', dest='input', required=True, help='Directorio con assets')
    p.add_argument('--output', '--output-dir', dest='output', required=False, default=None, help='Directorio de salida (por defecto: <input>_optimized)')
    p.add_argument('--formats', dest='formats', default='webp,avif', help='Formatos a generar (csv) e.g. webp,avif')
    p.add_argument('--sizes', dest='sizes', default='320,640,1280', help='Anchuras responsive a generar (csv)')
    p.add_argument('--video-presets', dest='video_presets', default='mp4:.mp4,webm:.webm', help='video presets como suffix:ext separados por coma, e.g. -mp4:.mp4,-webm:.webm')
    p.add_argument('--workers', dest='workers', type=int, default=4, help='Hilos para conversión')
    p.add_argument('--dry-run', dest='dry_run', action='store_true', help='No escribe archivos, solo simula (evalúa paths)')
    p.add_argument('--keep-larger', dest='keep_larger', action='store_true', help='Conservar variantes generadas aunque sean más grandes que el original')
    p.add_argument('--report', dest='report', default='report.json', help='Ruta al archivo JSON de informe')
    return p.parse_args()


def parse_video_presets(s: str) -> List[Tuple[str, str]]:
    out = []
    for part in s.split(','):
        if ':' in part:
            suffix, ext = part.split(':', 1)
            out.append((suffix, ext if ext.startswith('.') else '.' + ext))
    return out


def main():
    args = parse_args()
    input_dir = Path(args.input).resolve()
    if not input_dir.exists():
        print("Directorio de entrada no existe", input_dir)
        sys.exit(1)
    output_dir = Path(args.output).resolve() if args.output else input_dir.parent / (input_dir.name + '_optimized')
    formats = [f.strip().lower() for f in args.formats.split(',') if f.strip()]
    sizes = [int(x) for x in args.sizes.split(',') if x.strip()]
    video_presets = parse_video_presets(args.video_presets)

    print(f"Entrada: {input_dir}\nSalida: {output_dir}\nFormatos: {formats}\nTamaños: {sizes}\nVideo presets: {video_presets}")

    report = procesar_assets(input_dir, output_dir, formats, sizes, video_presets, args.workers, args.dry_run, args.keep_larger)
    guardar_reporte(report, Path(args.report))
    generate_html_snippets(report, output_dir / 'snippets.html')
    print("Reporte guardado en", args.report)
    print("Snippets guardados en", str(output_dir / 'snippets.html'))
    print(f"Total original: {human(report['total_original_bytes'])}")
    print(f"Total final: {human(report['total_final_bytes'])}")
    print(f"Saved: {human(report['total_saved_bytes'])} ({report['percent_reduction']:.2f}%)")


if __name__ == '__main__':
    main()
