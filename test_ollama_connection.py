#!/usr/bin/env python3
"""
Test Ollama API Connection
Simple script to test Ollama connectivity and list available models
"""

import os
import sys
import requests
import json

def test_ollama():
    OLLAMA_URL = os.getenv('OLLAMA_URL', 'https://ollama.jameskilby.cloud')
    OLLAMA_AUTH = os.getenv('OLLAMA_API_CREDENTIALS')
    MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    
    print(f"🔍 Testing Ollama API Connection")
    print(f"URL: {OLLAMA_URL}")
    print(f"Model: {MODEL}")
    print(f"Auth: {'Yes' if OLLAMA_AUTH else 'No'}")
    print("=" * 60)
    print()
    
    # Prepare auth
    auth_tuple = None
    if OLLAMA_AUTH and ':' in OLLAMA_AUTH:
        username, password = OLLAMA_AUTH.split(':', 1)
        auth_tuple = (username, password)
        print(f"✓ Using authentication: {username}:***")
    
    # Test 1: List models
    print("\n📋 Test 1: List Available Models")
    print("-" * 60)
    try:
        response = requests.get(
            f'{OLLAMA_URL}/api/tags',
            auth=auth_tuple,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            models = result.get('models', [])
            
            if models:
                print(f"✅ Found {len(models)} model(s):")
                for model in models:
                    name = model.get('name', 'unknown')
                    size = model.get('size', 0)
                    print(f"   - {name} ({size / 1e9:.2f} GB)")
            else:
                print("⚠️  No models found")
        elif response.status_code == 404:
            print("❌ Endpoint not found - check Ollama URL")
            print(f"   Response: {response.text[:200]}")
        elif response.status_code == 401:
            print("❌ Authentication failed")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {str(e)}")
        print("   Check that Ollama URL is correct and accessible")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 2: Try generate endpoint with the configured model
    print(f"\n🤖 Test 2: Test Generate Endpoint with '{MODEL}'")
    print("-" * 60)
    try:
        test_prompt = "Say hello in one word."
        
        response = requests.post(
            f'{OLLAMA_URL}/api/generate',
            json={
                'model': MODEL,
                'prompt': test_prompt,
                'stream': False,
                'options': {
                    'num_predict': 10
                }
            },
            auth=auth_tuple,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            print(f"✅ Success! Model responded:")
            print(f"   Response: {response_text[:100]}")
        elif response.status_code == 404:
            print(f"❌ Model '{MODEL}' not found")
            print(f"   Response: {response.text[:200]}")
            print()
            print("   Possible fixes:")
            print(f"   1. Pull the model: ollama pull {MODEL}")
            print(f"   2. Try different model name format:")
            
            # Try alternatives
            alternatives = []
            if ':' in MODEL:
                alternatives.append(MODEL.split(':')[0])
            else:
                alternatives.append(f"{MODEL}:latest")
                alternatives.append(f"{MODEL}:8b")
            
            for alt in alternatives:
                print(f"      - Try: OLLAMA_MODEL={alt}")
        elif response.status_code == 401:
            print("❌ Authentication failed")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (30s)")
        print("   Model might be loading or Ollama is slow")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Try alternative model names if original failed
    if response.status_code == 404:
        print(f"\n🔄 Test 3: Try Alternative Model Names")
        print("-" * 60)
        
        alternatives = []
        if ':' in MODEL:
            base = MODEL.split(':')[0]
            alternatives = [base, f"{base}:latest"]
        else:
            alternatives = [f"{MODEL}:latest", f"{MODEL}:8b"]
        
        for alt_model in alternatives:
            print(f"\nTrying: {alt_model}")
            try:
                response = requests.post(
                    f'{OLLAMA_URL}/api/generate',
                    json={
                        'model': alt_model,
                        'prompt': "Say hello in one word.",
                        'stream': False,
                        'options': {'num_predict': 10}
                    },
                    auth=auth_tuple,
                    timeout=20
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"✅ Success with '{alt_model}'!")
                    print(f"   Update your workflow to use: OLLAMA_MODEL={alt_model}")
                    break
                else:
                    print(f"❌ Failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete")

if __name__ == "__main__":
    test_ollama()
