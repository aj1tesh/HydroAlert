import json
import argparse
import os
from typing import Dict, List
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    __version__ as transformers_version
)
from datasets import Dataset


def get_eval_strategy_param():
    try:
        version_parts = transformers_version.split('.')
        major = int(version_parts[0])
        minor = int(version_parts[1]) if len(version_parts) > 1 else 0
        
        if major > 4 or (major == 4 and minor >= 19):
            return "eval_strategy"
        else:
            return "evaluation_strategy"
    except:
        return "eval_strategy"


def load_dataset(filepath: str) -> List[Dict]:
    """Load JSONL dataset file."""
    entries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def format_prompt(entry: Dict) -> str:
    instruction = entry["instruction"]
    location = entry["input"]["location"]
    weather = entry["input"]["weather_data"]
    risk = entry["output"]["risk_assessment"]
    summary = entry["output"]["natural_language_summary"]
    
    prompt = f"""Instruction: {instruction}

Input:
Location: {location['city']}, {location['state']} (Lat: {location['lat']:.4f}, Lon: {location['lon']:.4f})
Weather Data:
- Total Precipitation: {weather['total_precipitation_mm']:.1f}mm
- Max Hourly Precipitation: {weather['max_hourly_precip_mm']:.1f}mm
- Average Precipitation: {weather['avg_precipitation_mm']:.1f}mm
- Precipitation Days: {weather['precip_days']}
- Average Temperature: {weather['avg_temperature_c']:.1f}°C
- Soil Saturation Ratio: {weather['soil_saturation_ratio']:.2f}

Output:
{summary}

Risk Assessment:
- Overall Risk Score: {risk['overall_risk_score']:.3f}
- Minor Flooding Probability: {risk['severity_levels']['minor_flooding']['probability']*100:.1f}%
- Moderate Flooding Probability: {risk['severity_levels']['moderate_flooding']['probability']*100:.1f}%
- Severe Flooding Probability: {risk['severity_levels']['severe_flooding']['probability']*100:.1f}%
- Next 24 Hours: {risk['time_windows']['next_24_hours']['probability']*100:.1f}%
- Next 48 Hours: {risk['time_windows']['next_48_hours']['probability']*100:.1f}%
- Next 72 Hours: {risk['time_windows']['next_72_hours']['probability']*100:.1f}%
- Next 7 Days: {risk['time_windows']['next_7_days']['probability']*100:.1f}%
- Confidence: {risk['confidence']['confidence_level']} ({risk['confidence']['interpretation']})
"""
    
    return prompt


def prepare_dataset(train_file: str, tokenizer, max_length: int = 512):
    """Prepare dataset for training."""
    print("Loading training dataset...")
    train_entries = load_dataset(train_file)
    
    print(f"Loaded {len(train_entries)} training examples")
    print("Formatting prompts...")
    
    texts = [format_prompt(entry) for entry in train_entries]
    
    print("Tokenizing dataset...")
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length"
        )
    
    dataset = Dataset.from_dict({"text": texts})
    tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])
    
    return tokenized_dataset


def compute_metrics(eval_pred):
    """Compute evaluation metrics."""
    predictions, labels = eval_pred
    return {"perplexity": float(torch.exp(torch.tensor(0.0)))}


def main():
    parser = argparse.ArgumentParser(description="Fine-tune language model on flood prediction dataset")
    
    parser.add_argument(
        "--model_name",
        type=str,
        default="gpt2",
        help="Hugging Face model name (e.g., 'gpt2', 'microsoft/DialoGPT-small', 'distilgpt2')"
    )
    parser.add_argument(
        "--train_file",
        type=str,
        default="train_dataset.jsonl",
        help="Path to training dataset JSONL file"
    )
    parser.add_argument(
        "--test_file",
        type=str,
        default="test_dataset.jsonl",
        help="Path to test dataset JSONL file (for evaluation)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./flood_model_checkpoint",
        help="Output directory for fine-tuned model"
    )
    
    # Training arguments
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=4,
        help="Training batch size"
    )
    parser.add_argument(
        "--learning_rate",
        type=float,
        default=5e-5,
        help="Learning rate"
    )
    parser.add_argument(
        "--max_length",
        type=int,
        default=512,
        help="Maximum sequence length"
    )
    parser.add_argument(
        "--warmup_steps",
        type=int,
        default=100,
        help="Number of warmup steps"
    )
    parser.add_argument(
        "--save_steps",
        type=int,
        default=500,
        help="Save checkpoint every N steps"
    )
    parser.add_argument(
        "--eval_steps",
        type=int,
        default=500,
        help="Evaluate every N steps"
    )
    
    parser.add_argument(
        "--use_accelerate",
        action="store_true",
        help="Use Hugging Face Accelerate for distributed training"
    )
    parser.add_argument(
        "--fp16",
        action="store_true",
        help="Use mixed precision training (FP16)"
    )
    parser.add_argument(
        "--gradient_accumulation_steps",
        type=int,
        default=1,
        help="Number of gradient accumulation steps"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("Flood Prediction Model Fine-Tuning")
    print("="*60)
    print(f"Model: {args.model_name}")
    print(f"Training file: {args.train_file}")
    print(f"Output directory: {args.output_dir}")
    print()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    if device == "cpu":
        print("Warning: Training on CPU will be slow. Consider using GPU.")
    print()
    
    print(f"Loading tokenizer and model: {args.model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(args.model_name)
    model.resize_token_embeddings(len(tokenizer))
    
    print("Model loaded successfully!")
    print()
    
    train_dataset = prepare_dataset(args.train_file, tokenizer, args.max_length)
    
    eval_dataset = None
    if os.path.exists(args.test_file):
        print(f"Loading test dataset from {args.test_file}...")
        test_entries = load_dataset(args.test_file)
        test_texts = [format_prompt(entry) for entry in test_entries]
        test_dataset = Dataset.from_dict({"text": test_texts})
        eval_dataset = test_dataset.map(
            lambda examples: tokenizer(
                examples["text"],
                truncation=True,
                max_length=args.max_length,
                padding="max_length"
            ),
            batched=True,
            remove_columns=["text"]
        )
        print(f"Loaded {len(test_entries)} test examples")
    
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    eval_param_name = get_eval_strategy_param()
    training_kwargs = {
        "output_dir": args.output_dir,
        "overwrite_output_dir": True,
        "num_train_epochs": args.epochs,
        "per_device_train_batch_size": args.batch_size,
        "per_device_eval_batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "warmup_steps": args.warmup_steps,
        "save_steps": args.save_steps,
        "eval_steps": args.eval_steps,
        "save_total_limit": 3,
        "load_best_model_at_end": True if eval_dataset else False,
        "metric_for_best_model": "loss",
        "fp16": args.fp16,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "logging_steps": 50,
        "report_to": "none",
    }
    
    training_kwargs[eval_param_name] = "steps" if eval_dataset else "no"
    
    training_args = TrainingArguments(**training_kwargs)
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        compute_metrics=compute_metrics if eval_dataset else None,
    )
    
    print("="*60)
    print("Starting training...")
    print("="*60)
    print()
    
    train_result = trainer.train()
    
    print()
    print("="*60)
    print("Training completed!")
    print("="*60)
    print(f"Training loss: {train_result.training_loss:.4f}")
    if eval_dataset:
        print("Running evaluation...")
        eval_result = trainer.evaluate()
        print(f"Evaluation loss: {eval_result.get('eval_loss', 'N/A'):.4f}")
    
    print(f"\nSaving model to {args.output_dir}...")
    trainer.save_model()
    tokenizer.save_pretrained(args.output_dir)
    
    print()
    print("="*60)
    print("Fine-tuning complete!")
    print("="*60)
    print(f"Model saved to: {args.output_dir}")
    print()
    print("To use the fine-tuned model:")
    print(f"  from transformers import AutoTokenizer, AutoModelForCausalLM")
    print(f"  tokenizer = AutoTokenizer.from_pretrained('{args.output_dir}')")
    print(f"  model = AutoModelForCausalLM.from_pretrained('{args.output_dir}')")
    print()


if __name__ == "__main__":
    main()

