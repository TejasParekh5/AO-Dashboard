---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- generated_from_trainer
- dataset_size:79
- loss:CosineSimilarityLoss
widget:
- source_sentence: "\n        Application Owner: AO_022 (Alice Singh)\n        Applications:\
    \ Payroll Portal, Inventory Manager, Vendor Onboarding, Expense Tracker, CRM System\n\
    \        Critical/High vulnerabilities: 14\n        Open vulnerabilities: 10\n\
    \        Average closure time: 26.3 days\n        High risk items: 2\n       \
    \ Repeat issues average: 2.0\n        "
  sentences:
  - Regular security training for your team could help reduce vulnerability introduction.
  - There are 5 high-risk items (CVSS or Risk Score > 7) that require urgent attention.
  - Regular security training for your team could help reduce vulnerability introduction.
- source_sentence: "\n        Application Owner: AO_018 (Neha Rao)\n        Applications:\
    \ CRM System, Payroll Portal, Inventory Manager, Vendor Onboarding, Expense Tracker\n\
    \        Critical/High vulnerabilities: 17\n        Open vulnerabilities: 9\n\
    \        Average closure time: 23.4 days\n        High risk items: 4\n       \
    \ Repeat issues average: 1.9\n        "
  sentences:
  - Regular security training for your team could help reduce vulnerability introduction.
  - Regular security training for your team could help reduce vulnerability introduction.
  - You have 9 open vulnerabilities. Prioritize these for immediate remediation.
- source_sentence: "\n        Application Owner: AO_030 (Deepa Nair)\n        Applications:\
    \ Vendor Onboarding, Expense Tracker, CRM System, Inventory Manager, Payroll Portal\n\
    \        Critical/High vulnerabilities: 22\n        Open vulnerabilities: 11\n\
    \        Average closure time: 26.4 days\n        High risk items: 4\n       \
    \ Repeat issues average: 2.1\n        "
  sentences:
  - Regular security training for your team could help reduce vulnerability introduction.
  - Regular security training for your team could help reduce vulnerability introduction.
  - Focus on addressing the 15 high and critical vulnerabilities immediately.
- source_sentence: "\n        Application Owner: AO_028 (Sonal Desai)\n        Applications:\
    \ CRM System, Vendor Onboarding, Payroll Portal, Expense Tracker, Inventory Manager\n\
    \        Critical/High vulnerabilities: 11\n        Open vulnerabilities: 17\n\
    \        Average closure time: 24.4 days\n        High risk items: 1\n       \
    \ Repeat issues average: 1.8\n        "
  sentences:
  - Regular security training for your team could help reduce vulnerability introduction.
  - Focus on addressing the 14 high and critical vulnerabilities immediately.
  - There are 2 high-risk items (CVSS or Risk Score > 7) that require urgent attention.
- source_sentence: "\n        Application Owner: AO_018 (Neha Rao)\n        Applications:\
    \ CRM System, Payroll Portal, Inventory Manager, Vendor Onboarding, Expense Tracker\n\
    \        Critical/High vulnerabilities: 17\n        Open vulnerabilities: 9\n\
    \        Average closure time: 23.4 days\n        High risk items: 4\n       \
    \ Repeat issues average: 1.9\n        "
  sentences:
  - You have 11 open vulnerabilities. Prioritize these for immediate remediation.
  - You have 10 open vulnerabilities. Prioritize these for immediate remediation.
  - There are 4 high-risk items (CVSS or Risk Score > 7) that require urgent attention.
pipeline_tag: sentence-similarity
library_name: sentence-transformers
---

# SentenceTransformer

This is a [sentence-transformers](https://www.SBERT.net) model trained. It maps sentences & paragraphs to a 384-dimensional dense vector space and can be used for semantic textual similarity, semantic search, paraphrase mining, text classification, clustering, and more.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
<!-- - **Base model:** [Unknown](https://huggingface.co/unknown) -->
- **Maximum Sequence Length:** 128 tokens
- **Output Dimensionality:** 384 dimensions
- **Similarity Function:** Cosine Similarity
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/UKPLab/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'max_seq_length': 128, 'do_lower_case': False}) with Transformer model: BertModel 
  (1): Pooling({'word_embedding_dimension': 384, 'pooling_mode_cls_token': False, 'pooling_mode_mean_tokens': True, 'pooling_mode_max_tokens': False, 'pooling_mode_mean_sqrt_len_tokens': False, 'pooling_mode_weightedmean_tokens': False, 'pooling_mode_lasttoken': False, 'include_prompt': True})
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    '\n        Application Owner: AO_018 (Neha Rao)\n        Applications: CRM System, Payroll Portal, Inventory Manager, Vendor Onboarding, Expense Tracker\n        Critical/High vulnerabilities: 17\n        Open vulnerabilities: 9\n        Average closure time: 23.4 days\n        High risk items: 4\n        Repeat issues average: 1.9\n        ',
    'There are 4 high-risk items (CVSS or Risk Score > 7) that require urgent attention.',
    'You have 10 open vulnerabilities. Prioritize these for immediate remediation.',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities.shape)
# [3, 3]
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 79 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 79 samples:
  |         | sentence_0                                                                        | sentence_1                                                                         | label                                                         |
  |:--------|:----------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|:--------------------------------------------------------------|
  | type    | string                                                                            | string                                                                             | float                                                         |
  | details | <ul><li>min: 67 tokens</li><li>mean: 68.1 tokens</li><li>max: 69 tokens</li></ul> | <ul><li>min: 14 tokens</li><li>mean: 18.44 tokens</li><li>max: 23 tokens</li></ul> | <ul><li>min: 0.6</li><li>mean: 0.9</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                                                                                                                                                                                                                                                                                              | sentence_1                                                                                 | label            |
  |:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------|:-----------------|
  | <code><br>        Application Owner: AO_012 (Kavita Bose)<br>        Applications: Expense Tracker, Vendor Onboarding, CRM System, Inventory Manager, Payroll Portal<br>        Critical/High vulnerabilities: 19<br>        Open vulnerabilities: 14<br>        Average closure time: 26.6 days<br>        High risk items: 5<br>        Repeat issues average: 2.0<br>        </code> | <code>You have 14 open vulnerabilities. Prioritize these for immediate remediation.</code> | <code>1.0</code> |
  | <code><br>        Application Owner: AO_028 (Sonal Desai)<br>        Applications: CRM System, Vendor Onboarding, Payroll Portal, Expense Tracker, Inventory Manager<br>        Critical/High vulnerabilities: 11<br>        Open vulnerabilities: 17<br>        Average closure time: 24.4 days<br>        High risk items: 1<br>        Repeat issues average: 1.8<br>        </code> | <code>Focus on addressing the 11 high and critical vulnerabilities immediately.</code>     | <code>1.0</code> |
  | <code><br>        Application Owner: AO_020 (Pooja Reddy)<br>        Applications: Vendor Onboarding, Payroll Portal, Expense Tracker, Inventory Manager, CRM System<br>        Critical/High vulnerabilities: 18<br>        Open vulnerabilities: 11<br>        Average closure time: 24.8 days<br>        High risk items: 3<br>        Repeat issues average: 1.6<br>        </code> | <code>You have 11 open vulnerabilities. Prioritize these for immediate remediation.</code> | <code>1.0</code> |
* Loss: [<code>CosineSimilarityLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#cosinesimilarityloss) with these parameters:
  ```json
  {
      "loss_fct": "torch.nn.modules.loss.MSELoss"
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `num_train_epochs`: 10
- `multi_dataset_batch_sampler`: round_robin

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `overwrite_output_dir`: False
- `do_predict`: False
- `eval_strategy`: no
- `prediction_loss_only`: True
- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `per_gpu_train_batch_size`: None
- `per_gpu_eval_batch_size`: None
- `gradient_accumulation_steps`: 1
- `eval_accumulation_steps`: None
- `torch_empty_cache_steps`: None
- `learning_rate`: 5e-05
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `max_grad_norm`: 1
- `num_train_epochs`: 10
- `max_steps`: -1
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: {}
- `warmup_ratio`: 0.0
- `warmup_steps`: 0
- `log_level`: passive
- `log_level_replica`: warning
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `save_safetensors`: True
- `save_on_each_node`: False
- `save_only_model`: False
- `restore_callback_states_from_checkpoint`: False
- `no_cuda`: False
- `use_cpu`: False
- `use_mps_device`: False
- `seed`: 42
- `data_seed`: None
- `jit_mode_eval`: False
- `use_ipex`: False
- `bf16`: False
- `fp16`: False
- `fp16_opt_level`: O1
- `half_precision_backend`: auto
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `local_rank`: 0
- `ddp_backend`: None
- `tpu_num_cores`: None
- `tpu_metrics_debug`: False
- `debug`: []
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_prefetch_factor`: None
- `past_index`: -1
- `disable_tqdm`: False
- `remove_unused_columns`: True
- `label_names`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `fsdp`: []
- `fsdp_min_num_params`: 0
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `fsdp_transformer_layer_cls_to_wrap`: None
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `deepspeed`: None
- `label_smoothing_factor`: 0.0
- `optim`: adamw_torch
- `optim_args`: None
- `adafactor`: False
- `group_by_length`: False
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `skip_memory_metrics`: True
- `use_legacy_prediction_loop`: False
- `push_to_hub`: False
- `resume_from_checkpoint`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_private_repo`: None
- `hub_always_push`: False
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `include_inputs_for_metrics`: False
- `include_for_metrics`: []
- `eval_do_concat_batches`: True
- `fp16_backend`: auto
- `push_to_hub_model_id`: None
- `push_to_hub_organization`: None
- `mp_parameters`: 
- `auto_find_batch_size`: False
- `full_determinism`: False
- `torchdynamo`: None
- `ray_scope`: last
- `ddp_timeout`: 1800
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `include_tokens_per_second`: False
- `include_num_input_tokens_seen`: False
- `neftune_noise_alpha`: None
- `optim_target_modules`: None
- `batch_eval_metrics`: False
- `eval_on_start`: False
- `use_liger_kernel`: False
- `eval_use_gather_object`: False
- `average_tokens_across_devices`: False
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: round_robin

</details>

### Framework Versions
- Python: 3.11.8
- Sentence Transformers: 4.1.0
- Transformers: 4.52.4
- PyTorch: 2.5.1+cpu
- Accelerate: 1.7.0
- Datasets: 2.15.0
- Tokenizers: 0.21.1

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->