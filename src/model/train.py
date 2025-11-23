import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig
from trl import SFTTrainer

class ModelTrainer:
    def __init__(self, model_name="google/gemma-2b-it", output_dir="outputs"):
        self.model_name = model_name
        self.output_dir = output_dir
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def train(self, dataset_path, max_seq_length=512, num_train_epochs=1):
        print(f"Starting training with {self.model_name}...")
        
        # 1. Load Dataset
        dataset = load_dataset("json", data_files=dataset_path, split="train")
        
        # 2. Quantization Config
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        
        # 3. Load Model
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto",
            token=os.environ.get("HF_TOKEN")
        )
        
        tokenizer = AutoTokenizer.from_pretrained(self.model_name, token=os.environ.get("HF_TOKEN"))
        tokenizer.pad_token = tokenizer.eos_token
        
        # 4. LoRA Config
        peft_config = LoraConfig(
            r=8,
            lora_alpha=16,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj']
        )
        
        # 5. Training Arguments
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            optim="paged_adamw_8bit",
            logging_steps=10,
            learning_rate=2e-4,
            fp16=True,
            max_grad_norm=0.3,
            num_train_epochs=num_train_epochs,
            warmup_ratio=0.03,
            group_by_length=True,
            lr_scheduler_type="constant",
        )
        
        # 6. Trainer
        trainer = SFTTrainer(
            model=model,
            train_dataset=dataset,
            peft_config=peft_config,
            dataset_text_field="input_text", # We formatted it as 'input_text' in preprocess
            max_seq_length=max_seq_length,
            tokenizer=tokenizer,
            args=training_args,
            packing=False,
        )
        
        trainer.train()
        trainer.save_model(self.output_dir)
        print(f"Model saved to {self.output_dir}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_path", type=str, default="processed_dataset.jsonl")
    parser.add_argument("--epochs", type=int, default=1)
    args = parser.parse_args()
    
    trainer = ModelTrainer()
    trainer.train(args.dataset_path, num_train_epochs=args.epochs)
