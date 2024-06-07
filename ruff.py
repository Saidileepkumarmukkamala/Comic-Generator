from diffusers import DiffusionPipeline
import torch

pipe = DiffusionPipeline.from_pretrained('stabilityai/stable-diffusion-xl-base-1.0', torch_dtype = torch.float16, variant = 'fp16')
pipe.to('cuda')
prompt = "The quick brown fox jumps over the lazy dog."
image = pipe(prompt=prompt).images[0]
image.save('ruff.png')