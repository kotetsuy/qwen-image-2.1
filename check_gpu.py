"""Small ROCm correctness checks; no model download required."""
import json
import torch
import torch.nn.functional as F


def main():
    assert torch.version.hip, "ROCm-enabled PyTorch is required"
    assert torch.cuda.is_available(), "GPU is unavailable"
    torch.manual_seed(42)
    props = torch.cuda.get_device_properties(0)
    a = torch.randn(256, 256, dtype=torch.bfloat16)
    b = torch.randn(256, 256, dtype=torch.bfloat16)
    actual = (a.cuda() @ b.cuda()).float().cpu()
    expected = a.float() @ b.float()
    torch.testing.assert_close(actual, expected, rtol=0.02, atol=0.25)
    q, k, v = [torch.randn(1, 4, 128, 64, dtype=torch.bfloat16) for _ in range(3)]
    attention = F.scaled_dot_product_attention(q.cuda(), k.cuda(), v.cuda()).float().cpu()
    reference = F.scaled_dot_product_attention(q.float(), k.float(), v.float())
    torch.testing.assert_close(attention, reference, rtol=0.03, atol=0.02)
    torch.cuda.synchronize()
    from diffusers import QwenImage21Pipeline
    import transformers
    import diffusers
    print(json.dumps({
        "torch": torch.__version__, "hip": torch.version.hip,
        "gpu": props.name, "architecture": props.gcnArchName,
        "gpu_memory_gib": props.total_memory / 2**30,
        "bf16_matmul": "PASS", "sdpa": "PASS",
        "pipeline_import": QwenImage21Pipeline.__name__,
        "transformers": transformers.__version__, "diffusers": diffusers.__version__,
    }, indent=2))


if __name__ == "__main__":
    main()
