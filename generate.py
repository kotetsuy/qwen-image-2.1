"""Generate an image with the local Qwen-Image-2.1 checkpoint."""
import argparse
import json
from pathlib import Path
import time

import torch
from diffusers import QwenImage21Pipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='models/Qwen-Image-2.1')
    prompt_group = parser.add_mutually_exclusive_group()
    prompt_group.add_argument('--prompt', help='Prompt text')
    prompt_group.add_argument('--prompt-file', help='UTF-8 text file containing the prompt')
    parser.add_argument('--output', default='outputs/first-image.png')
    parser.add_argument('--size', type=int, default=512)
    parser.add_argument('--steps', type=int, default=20)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    if args.prompt_file is not None:
        try:
            args.prompt = Path(args.prompt_file).read_text(encoding='utf-8-sig').strip()
        except (OSError, UnicodeError) as exc:
            parser.error(f'Cannot read prompt file {args.prompt_file!r}: {exc}')
        if not args.prompt:
            parser.error('Prompt file must not be empty or whitespace-only')
    elif args.prompt is None:
        args.prompt = 'A small red fox sitting in a peaceful green forest, soft morning sunlight, detailed natural photography.'
    assert torch.cuda.is_available() and torch.version.hip, 'ROCm GPU required'
    start = time.monotonic()
    pipe = QwenImage21Pipeline.from_pretrained(
        args.model, torch_dtype=torch.bfloat16, local_files_only=True,
    )
    pipe.enable_model_cpu_offload()
    pipe.vae.enable_tiling()
    loaded = time.monotonic()
    torch.cuda.reset_peak_memory_stats()
    image = pipe(
        prompt=args.prompt, width=args.size, height=args.size,
        num_inference_steps=args.steps,
        generator=torch.Generator('cuda').manual_seed(args.seed),
    ).images[0]
    torch.cuda.synchronize()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    report = dict(vars(args), load_seconds=loaded-start,
                  generation_seconds=time.monotonic()-loaded,
                  peak_gpu_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
                  peak_gpu_reserved_gib=torch.cuda.max_memory_reserved()/2**30,
                  image_size=list(image.size), image_mode=image.mode,
                  torch=torch.__version__, hip=torch.version.hip)
    output.with_suffix('.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
