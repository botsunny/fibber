import pytest
import torch

from fibber.benchmark import Benchmark
from fibber.paraphrase_strategies import ASRSStrategy, TextAttackStrategy


@pytest.fixture()
def gpu_id():
    if torch.cuda.device_count() > 0:
        return 0
    return -1


@pytest.mark.slow
def test_integrity_identity(gpu_id):
    torch.cuda.empty_cache()
    benchmark = Benchmark(
        output_dir="exp-pytest",
        dataset_name="mr",
        subsample_attack_set=100,
        use_gpu_id=gpu_id,
        gpt2_gpu_id=gpu_id,
        transformer_clf_gpu_id=gpu_id,
        transformer_clf_steps=5000,
        transformer_clf_bs=32
    )

    result = benchmark.run_benchmark(paraphrase_strategy="IdentityStrategy")
    assert result["bert-base-uncased-Classifier_Accuracy_targeted(↓)"] > 0.85


@pytest.mark.slow
def test_integrity_textfooler(gpu_id):
    torch.cuda.empty_cache()
    benchmark = Benchmark(
        output_dir="exp-pytest",
        dataset_name="mr",
        subsample_attack_set=100,
        use_gpu_id=gpu_id,
        gpt2_gpu_id=gpu_id,
        transformer_clf_gpu_id=gpu_id,
        transformer_clf_steps=5000,
        transformer_clf_bs=32
    )

    strategy = TextAttackStrategy(
        arg_dict={"ta_recipe": "TextFoolerJin2019"},
        dataset_name="mr",
        strategy_gpu_id=gpu_id,
        output_dir="exp-pytest",
        metric_bundle=benchmark.get_metric_bundle())
    result = benchmark.run_benchmark(paraphrase_strategy=strategy)

    assert result["bert-base-uncased-Classifier_Accuracy_targeted(↓)"] < 0.50


@pytest.mark.slow
def test_integrity_bertsampling(gpu_id):
    torch.cuda.empty_cache()
    benchmark = Benchmark(
        output_dir="exp-pytest",
        dataset_name="mr",
        subsample_attack_set=1,
        use_gpu_id=gpu_id,
        gpt2_gpu_id=gpu_id,
        transformer_clf_gpu_id=gpu_id,
        transformer_clf_steps=5000,
        transformer_clf_bs=32
    )
    strategy = ASRSStrategy(
        arg_dict={"bs_lm_steps": 1000},
        dataset_name="mr",
        strategy_gpu_id=gpu_id,
        output_dir="exp-pytest",
        metric_bundle=benchmark.get_metric_bundle())
    benchmark.run_benchmark(paraphrase_strategy=strategy, num_paraphrases_per_text=10)
