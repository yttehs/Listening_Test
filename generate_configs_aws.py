import os
import json
from pathlib import Path

# CONFIGURATION - UPDATE THESE
S3_BUCKET_NAME = "listening-test-audio-files"  # UPDATE with your S3 bucket name
S3_REGION = "us-west-1"  # UPDATE with your S3 region (e.g., us-east-1, us-west-2)
BASE_PATH = "/Users/vishwas/Desktop/Github/Listening_Test"  # UPDATE with your local folder path

# S3 URL format
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com"

# Define all trial folder names
GENDERS = ["Male", "Female"]
STYLES = ["read", "conv"]
MG_COMBINATIONS = ["MG1_MG2", "MG1_MG3", "MG1_MG4", "MG2_MG3", "MG2_MG4", "MG3_MG4"]

def generate_trial_folders():
    """Generate all 24 trial folder names"""
    trials = []
    for gender in GENDERS:
        for style in STYLES:
            for mg_combo in MG_COMBINATIONS:
                trial_name = f"{gender}_{style}_{mg_combo}"
                trials.append(trial_name)
    return trials

def get_audio_files(trial_folder_path):
    """Get all audio files from a trial folder, sorted alphabetically"""
    audio_files = []
    folder = Path(trial_folder_path)
    
    if not folder.exists():
        print(f"Warning: Folder {trial_folder_path} does not exist!")
        return []
    
    # Get all audio files (wav or mp3)
    for ext in ['*.wav', '*.mp3']:
        for file in sorted(folder.glob(ext)):
            audio_files.append(file.name)
    
    return audio_files

def create_config_json(trial_name, audio_files):
    """Create config.json content for a trial with S3 URLs"""
    config = {
        "trialId": trial_name,
        "audioFiles": []
    }
    
    for idx, filename in enumerate(audio_files):
        # S3 URL format
        audio_url = f"{S3_BASE_URL}/{trial_name}/{filename}"
        
        config["audioFiles"].append({
            "circle": idx + 1,
            "filename": filename,
            "url": audio_url
        })
    
    return config

def save_config_file(trial_folder_path, config_data):
    """Save config.json to the trial folder"""
    config_path = Path(trial_folder_path) / "config.json"
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created config.json for {Path(trial_folder_path).name}")

def generate_all_configs():
    """Main function to generate config files for all trials"""
    trial_folders = generate_trial_folders()
    
    print(f"Generating S3-based config files for {len(trial_folders)} trials...\n")
    print(f"S3 Bucket: {S3_BUCKET_NAME}")
    print(f"S3 Region: {S3_REGION}")
    print(f"Base URL: {S3_BASE_URL}\n")
    
    summary = []
    
    for trial_name in trial_folders:
        trial_path = Path(BASE_PATH) / trial_name
        
        # Get audio files
        audio_files = get_audio_files(trial_path)
        
        if not audio_files:
            print(f"✗ Skipped {trial_name} (no audio files found)")
            continue
        
        # Create config
        config_data = create_config_json(trial_name, audio_files)
        
        # Save config file
        save_config_file(trial_path, config_data)
        
        summary.append({
            "trial": trial_name,
            "num_files": len(audio_files)
        })
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for item in summary:
        print(f"{item['trial']}: {item['num_files']} audio files")
    print(f"\nTotal trials processed: {len(summary)}")
    print("="*60)

def generate_trials_list():
    """Generate a JSON file with all trial information for the web app"""
    trial_folders = generate_trial_folders()
    trials_list = []
    
    for trial_name in trial_folders:
        trial_path = Path(BASE_PATH) / trial_name
        audio_files = get_audio_files(trial_path)
        
        if audio_files:
            trials_list.append({
                "id": trial_name,
                "name": trial_name.replace("_", " "),
                "numFiles": len(audio_files)
            })
    
    # Save trials list
    trials_list_path = Path(BASE_PATH) / "trials_list.json"
    with open(trials_list_path, 'w', encoding='utf-8') as f:
        json.dump({"trials": trials_list}, f, indent=2)
    
    print(f"\n✓ Created trials_list.json with {len(trials_list)} trials")

if __name__ == "__main__":
    print("Voice Perception Test - S3 Config Generator")
    print("="*60 + "\n")
    
    # Validate configuration
    if BASE_PATH == "/path/to/your/Listening_Test":
        print("ERROR: Please update BASE_PATH in the script!")
        print("Example: BASE_PATH = '/Users/yourname/Documents/Listening_Test'")
        exit(1)
    
    if S3_BUCKET_NAME == "listening-test-audio-files":
        print("WARNING: Using default bucket name 'listening-test-audio-files'")
        print("Make sure this matches your actual S3 bucket name!\n")
    
    if S3_REGION == "us-west-2":
        print("WARNING: Using default region 'us-west-2'")
        print("Make sure this matches your S3 bucket region!\n")
    
    # Generate all config files
    generate_all_configs()
    
    # Generate trials list
    generate_trials_list()
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Upload all trial folders (with new config.json) to S3")
    print("2. Upload trials_list.json to S3")
    print("3. Make sure bucket policy allows public read access")
    print("4. Test loading audio in your web app")
    print("="*60)
