#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path
import logging

def main():
    parser = argparse.ArgumentParser(description='Manage the LLM cache')
    parser.add_argument('--action', type=str, choices=['clear', 'view', 'stats'], 
                        default='stats', help='Action to perform on the cache')
    parser.add_argument('--type', type=str, choices=['all', 'response', 'embedding'], 
                        default='all', help='Type of cache to operate on')
    parser.add_argument('--cache-dir', type=str, default='llm_cache', 
                        help='Directory containing the cache files')
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    cache_dir = Path(args.cache_dir)
    response_cache_file = cache_dir / "response_cache.json"
    embedding_cache_file = cache_dir / "embedding_cache_file.json"
    
    if args.action == 'clear':
        clear_cache(args.type, response_cache_file, embedding_cache_file)
    elif args.action == 'view':
        view_cache(args.type, response_cache_file, embedding_cache_file)
    elif args.action == 'stats':
        show_cache_stats(args.type, response_cache_file, embedding_cache_file)

def clear_cache(cache_type, response_cache_file, embedding_cache_file):
    if cache_type in ['all', 'response']:
        if response_cache_file.exists():
            with open(response_cache_file, 'w') as f:
                json.dump({}, f)
            print(f"Response cache cleared: {response_cache_file}")
        else:
            print(f"Response cache file not found: {response_cache_file}")
    
    if cache_type in ['all', 'embedding']:
        if embedding_cache_file.exists():
            with open(embedding_cache_file, 'w') as f:
                json.dump({}, f)
            print(f"Embedding cache cleared: {embedding_cache_file}")
        else:
            print(f"Embedding cache file not found: {embedding_cache_file}")
    
    if cache_type == 'all':
        print("All caches cleared.")

def view_cache(cache_type, response_cache_file, embedding_cache_file):
    if cache_type in ['all', 'response']:
        if response_cache_file.exists():
            with open(response_cache_file, 'r') as f:
                response_cache = json.load(f)
            print(f"Response cache ({len(response_cache)} entries):")
            for i, (key, value) in enumerate(response_cache.items()):
                print(f"  {i+1}. {key}: {value[:50]}...")
        else:
            print(f"Response cache file not found: {response_cache_file}")
    
    if cache_type in ['all', 'embedding']:
        if embedding_cache_file.exists():
            with open(embedding_cache_file, 'r') as f:
                embedding_cache = json.load(f)
            print(f"Embedding cache:")
            for key, value in embedding_cache.items():
                print(f"  {key}: {value}")
        else:
            print(f"Embedding cache file not found: {embedding_cache_file}")

def show_cache_stats(cache_type, response_cache_file, embedding_cache_file):
    if cache_type in ['all', 'response']:
        if response_cache_file.exists():
            with open(response_cache_file, 'r') as f:
                response_cache = json.load(f)
            print(f"Response cache: {len(response_cache)} entries")
            print(f"  File size: {os.path.getsize(response_cache_file) / 1024:.2f} KB")
        else:
            print(f"Response cache file not found: {response_cache_file}")
    
    if cache_type in ['all', 'embedding']:
        if embedding_cache_file.exists():
            with open(embedding_cache_file, 'r') as f:
                embedding_cache = json.load(f)
            print(f"Embedding cache: {len(embedding_cache)} entries")
            print(f"  File size: {os.path.getsize(embedding_cache_file) / 1024:.2f} KB")
        else:
            print(f"Embedding cache file not found: {embedding_cache_file}")

if __name__ == "__main__":
    main()