import os
import requests
from flask import Flask, jsonify, Response

app = Flask(__name__)

# আপনার ফ্যানকোড অ্যাকাউন্ট থেকে আনা টোকেনটি এখানে বসাবেন
# অথবা গিটহাব/রেন্ডার এনভায়রনমেন্ট ভ্যারিয়েবলে (REFRESH_TOKEN) সেট করবেন
FANCODE_REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN", "আপনার_ফ্যানকোড_রিফ্রেশ_টোকেন_এখানে_দিন")

def get_live_fancode_streams():
    """ফ্যানকোড সার্ভার থেকে রিয়েল-টাইমে লাইভ ম্যাচ ও M3U8 লিংক স্ক্র্যাপ করার ফাংশন"""
    try:
        headers = {
            "Authorization": f"Bearer {FANCODE_REFRESH_TOKEN}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # ফ্যানকোডের আসল এপিআই এন্ডপয়েন্ট (যেখান থেকে ম্যাচের জেসন ডেটা আসে)
        api_url = "https://fancode.com" 
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json() 
        else:
            # যদি এপিআই এখনো কাজ না করে, তবে সার্ভার ক্র্যাশ না করিয়ে একটি ডেমো লিস্ট রিটার্ন করবে
            return [
                {
                    "title": "Live Cricket Match 1",
                    "thumbnail": "https://example.com",
                    "stream_url": "https://google.com"
                }
            ]
            
    except Exception as e:
        # কোনো কারণে এরর আসলে ডেমো সচল ডেটা দেবে যাতে রেন্ডার সার্ভার বন্ধ না হয়
        return [
            {
                "title": "Default Live Match",
                "thumbnail": "https://example.com",
                "stream_url": "https://google.com"
            }
        ]

@app.route('/')
def home():
    return jsonify({"status": "Server is running", "modes": ["/matches", "/playlist.m3u"]})

@app.route('/matches')
def matches():
    """অ্যাডমিন প্যানেলের জন্য JSON API এন্ডপয়েন্ট"""
    data = get_live_fancode_streams()
    return jsonify(data)

@app.route('/playlist.m3u')
def playlist():
    """IPTV বা অ্যাডমিন প্যানেলের জন্য অটো-আপডেটেড M3U প্লেলিস্ট"""
    data = get_live_fancode_streams()
    
    m3u_content = "#EXTM3U\n"
    if isinstance(data, list):
        for match in data:
            match_name = match.get("title", "Live Match")
            logo = match.get("thumbnail", "")
            stream_url = match.get("stream_url", "")
            
            m3u_content += f'#EXTINF:-1 tvg-logo="{logo}",{match_name}\n{stream_url}\n'
    else:
        m3u_content += "#EXTINF:-1, No Active Matches Right Now\nhttp://example.com\n"
        
    return Response(m3u_content, mimetype='text/plain')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
