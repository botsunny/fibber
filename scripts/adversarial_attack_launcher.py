import argparse
import copy
import subprocess

COMMON_CONFIG = {
    "--subsample_testset": 1000,
    "--num_paraphrases_per_text": 50,
    "--robust_tuning": "0",
    # ignored when robut_tuning is 0 and load_robust_tuned_clf is not set
    "--robust_tuning_steps": 5000,
    # "--target_classifier": "fasttext",
    "--target_classifier": "transformer",
    # "--transformer_clf_model_init": "roberta-large"
}

DEFENSE_CONFIG = {
    "none": {},
    "sem": {
        "--transformer_clf_enable_sem": "1"
    },
    "lmag": {
        "--transformer_clf_enable_lmag": "1"
    }
}

GPU_CONFIG = {
    "0": {
        "--transformer_clf_gpu_id": 0,
        "--bert_ppl_gpu_id": 0,
        "--use_gpu_id": 0,
        "--gpt2_gpu_id": 0,
        "--strategy_gpu_id": 0,
        "--ce_gpu_id": 0
    },
    "1": {
        "--transformer_clf_gpu_id": 1,
        "--bert_ppl_gpu_id": 1,
        "--use_gpu_id": 1,
        "--gpt2_gpu_id": 1,
        "--ce_gpu_id": 1,
        "--strategy_gpu_id": 1,
    },
    "2": {
        "--transformer_clf_gpu_id": 2,
        "--bert_ppl_gpu_id": 2,
        "--use_gpu_id": 2,
        "--gpt2_gpu_id": 2,
        "--ce_gpu_id": 2,
        "--strategy_gpu_id": 2,
    },
    "3": {
        "--transformer_clf_gpu_id": 3,
        "--bert_ppl_gpu_id": 3,
        "--use_gpu_id": 3,
        "--gpt2_gpu_id": 3,
        "--ce_gpu_id": 3,
        "--strategy_gpu_id": 3,
    }
}

DATASET_CONFIG = {
    "ag_no_title": {
        "--dataset": "ag_no_title",
        "--output_dir": "exp-ag_no_title",
        "--transformer_clf_steps": 20000
    },
    "mr": {
        "--dataset": "mr",
        "--output_dir": "exp-mr",
        "--transformer_clf_steps": 5000
    },
    "sst2": {
        "--dataset": "sst2",
        "--output_dir": "exp-sst2",
        "--transformer_clf_steps": 20000
    },
    "trec": {
        "--dataset": "trec",
        "--output_dir": "exp-trec",
        "--transformer_clf_steps": 5000
    },
    "hate": {
        "--dataset": "hate",
        "--output_dir": "exp-hate",
        "--transformer_clf_steps": 20000
    },
    "fn_short": {
        "--dataset": "fn_short",
        "--output_dir": "exp-fn_short",
        "--transformer_clf_steps": 20000
    },
    "fake_review_cg": {
        "--dataset": "fake_review_cg",
        "--output_dir": "exp-fake_review_cg",
        "--transformer_clf_steps": 20000
    },
    "fake_news": {
        "--dataset": "fake_news",
        "--output_dir": "exp-fake_news",
        "--transformer_clf_steps": 20000
    },
}

STRATEGY_CONFIG = {
    "identity": {
        "--strategy": "IdentityStrategy"
    },
    "textfooler": {
        "--strategy": "TextAttackStrategy",
        "--ta_recipe": "TextFoolerJin2019",
        "--robust_tune_num_attack_per_step": 20
    },
    "pso": {
        "--strategy": "OpenAttackStrategy",
        "--oa_recipe": "PSOAttacker",
        "--robust_tune_num_attack_per_step": 5
    },
    "bertattack": {
        "--strategy": "TextAttackStrategy",
        "--ta_recipe": "BERTAttackLi2020",
        "--robust_tune_num_attack_per_step": 5
    },
    "bertattack-oa": {
        "--strategy": "OpenAttackStrategy",
        "--oa_recipe": "BERTAttacker",
        "--robust_tune_num_attack_per_step": 5
    },
    "bae": {
        "--strategy": "TextAttackStrategy",
        "--ta_recipe": "BAEGarg2019",
        "--robust_tune_num_attack_per_step": 5
    },
    "clare": {
        "--strategy": "TextAttackStrategy",
        "--ta_recipe": "CLARE2020",
        "--robust_tune_num_attack_per_step": 16
    },
    "a2t": {
        "--strategy": "TextAttackStrategy",
        "--ta_recipe": "A2TYoo2021",
    },
    "scpn": {
        "--strategy": "OpenAttackStrategy",
        "--oa_recipe": "SCPNAttacker",
        "--robust_tune_num_attack_per_step": 5
    },
    "gsa": {
        "--strategy": "TextAttackStrategy",
        "--ta_recipe": "Kuleshov2017",
        "--robust_tune_num_attack_per_step": 5
    },
    "pwws": {
        "--strategy": "TextAttackStrategy",
        "--ta_recipe": "PWWSRen2019",
        "--robust_tune_num_attack_per_step": 5
    },
    "asrs": {
        "--strategy": "ASRSStrategy",
        "--asrs_enforcing_dist": "wpe",
        "--asrs_wpe_threshold": 1.0,
        "--asrs_wpe_weight": 1000,
        "--asrs_sim_threshold": 1.0,
        "--asrs_sim_weight": 500,
        "--asrs_ppl_weight": 100,
        "--asrs_sampling_steps": 50,
        "--asrs_burnin_steps": 0,
        "--asrs_clf_weight": 3,
        "--asrs_window_size": 3,
        "--asrs_accept_criteria": "joint_weighted_criteria",
        "--asrs_burnin_enforcing_schedule": "1",
        "--asrs_burnin_criteria_schedule": "1",
        "--asrs_seed_option": "dynamic_len",
        "--asrs_lm_option": "finetune",
        "--asrs_sim_metric": "CESimilarityMetric",
        "--robust_tune_num_attack_per_step": 5
    },
    "fu": {
        "--strategy": "FudgeStrategy",
    },
    "rr": {
        "--strategy": "RewriteRollbackStrategy",
        "--rr_enforcing_dist": "wpe",
        "--rr_wpe_threshold": 1.0,
        "--rr_wpe_weight": 5,
        "--rr_sim_threshold": 0.95,
        "--rr_sim_weight": 20,
        "--rr_ppl_weight": 5,
        "--rr_sampling_steps": 200,
        "--rr_clf_weight": 2,
        "--rr_window_size": 3,
        "--rr_accept_criteria": "joint_weighted_criteria",
        "--rr_lm_option": "finetune",
        "--rr_sim_metric": "USESimilarityMetric",
        "--rr_early_stop": "half",
        "--robust_tune_num_attack_per_step": 16
    },
    "sap": {
        "--strategy": "SapStrategy"
    },
    "rm": {
        "--strategy": "RemoveStrategy"
    }
}


def to_command(args):
    ret = []
    for k, v in args.items():
        ret.append(k)
        ret.append(str(v))

    return ret


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--gpu", choices=list(GPU_CONFIG.keys()), default="0")
    parser.add_argument("--dataset", choices=list(DATASET_CONFIG.keys()) + ["all"], default="all")
    parser.add_argument("--strategy", choices=list(STRATEGY_CONFIG.keys()) + ["all"],
                        default="all")
    parser.add_argument("--robust_desc", type=str, default=None)
    parser.add_argument("--robust_steps", type=int, default=5000)
    parser.add_argument("--robust_tuning", type=str, default="0")
    parser.add_argument("--defense", type=str, default="none")
    parser.add_argument("--exp_name", type=str, default=None)
    parser.add_argument("--model_init", type=str, default="bert-base")

    args = parser.parse_args()

    if args.robust_tuning == "1":
        COMMON_CONFIG["--robust_tuning"] = "1"

    if args.dataset == "all":
        dataset_list = list(DATASET_CONFIG.keys())
    else:
        dataset_list = [args.dataset]

    if args.strategy == "all":
        strategy_list = list(STRATEGY_CONFIG.keys())
    else:
        strategy_list = [args.strategy]

    for dataset in dataset_list:
        for strategy in strategy_list:
            command = ["python3", "-m", "fibber.benchmark.benchmark_adversarial_attack"]

            command += ["--transformer_clf_model_init", args.model_init]

            if args.exp_name is not None:
                command += ["--exp_name", args.exp_name]

            command += to_command(COMMON_CONFIG)
            command += to_command(GPU_CONFIG[args.gpu])
            command += to_command(DATASET_CONFIG[dataset])
            command += to_command(DEFENSE_CONFIG[args.defense])

            if args.robust_desc is not None:
                command += to_command({"--load_robust_tuned_clf_desc": args.robust_desc})
                idx = command.index("--robust_tuning_steps")
                command[idx + 1] = str(args.robust_steps)

            if strategy[:4] == "asrs":
                strategy_config_tmp = copy.copy(STRATEGY_CONFIG["asrs"])
                if strategy != "asrs":
                    for k, v in STRATEGY_CONFIG[strategy].items():
                        strategy_config_tmp[k] = v
                command += to_command(strategy_config_tmp)
            else:
                command += to_command(STRATEGY_CONFIG[strategy])
            subprocess.call(command)


if __name__ == "__main__":
    main()
