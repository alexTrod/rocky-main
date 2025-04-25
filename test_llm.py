#!/usr/bin/env python3

from llm_handler import LLMHandler
import argparse

def main():
    parser = argparse.ArgumentParser(description='Test the LLM Handler')
    parser.add_argument('--question', type=str, help='Question to ask the LLM')
    args = parser.parse_args()
    
    print("Initializing LLM Handler...")
    llm = LLMHandler()
    
    if args.question:
        print(f"Question: {args.question}")
        answer = llm.ask_question(args.question)
        print(f"Answer: {answer}")
    else:
        print("Entering interactive mode. Type 'exit' to quit.")
        while True:
            question = input("\nEnter your question: ")
            if question.lower() in ['exit', 'quit', 'q']:
                break
            
            answer = llm.ask_question(question)
            print(f"\nAnswer: {answer}")

if __name__ == "__main__":
    main()