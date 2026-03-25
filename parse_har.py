import json

# Extract full headers for the sign-in action endpoints
files_and_urls = {
    '签到赢好礼': (r'c:\Users\Administrator\Desktop\签到\签到赢好礼并点击签到.har', 'h5-act/signIn/init'),
    '金币乐园打卡': (r'c:\Users\Administrator\Desktop\签到\金币乐园并点击打卡.har', 'h5-act/goldSignIn/signIn'),
    '签到有礼': (r'c:\Users\Administrator\Desktop\签到\签到有礼并点击签到.har', 'mark31/domark'),
}

for name, (path, url_pattern) in files_and_urls.items():
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n{'='*60}")
    print(f"=== {name} ({url_pattern}) ===")
    
    for entry in data['log']['entries']:
        req = entry['request']
        if url_pattern in req['url']:
            print(f"Method: {req['method']}")
            print(f"Full URL: {req['url']}")
            print(f"\nAll Headers:")
            for h in req['headers']:
                if h['name'].lower() not in ['accept-encoding', 'connection', 'accept-language']:
                    print(f"  {h['name']}: {h['value'][:150]}")
            if req.get('postData'):
                print(f"\nPayload: {req['postData'].get('text', '')}")
            resp = entry['response']
            print(f"\nResponse Status: {resp['status']}")
            print(f"Response: {resp['content'].get('text', '')[:500]}")
            break  # Only need the first match
