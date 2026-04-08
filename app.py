import os
import json
from flask import Flask, request, jsonify, render_template_string
from anthropic import Anthropic

app = Flask(__name__)
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

PLANS = {
    "basic": {"name": "Basic", "price": 12, "newsletters": 4, "detail": "4 newsletters/month"},
    "pro": {"name": "Pro", "price": 29, "newsletters": 12, "detail": "12 newsletters/month"},
    "agency": {"name": "Agency", "price": 49, "newsletters": "unlimited", "detail": "Unlimited newsletters"},
}

SYSTEM_PROMPT = """You are NewsletterPro AI, an expert email newsletter writer. Given a topic, audience, tone, and length, generate a complete newsletter in valid JSON:
{
  "subject_line": "string",
  "preview_text": "string",
  "header": {"title": "string", "subtitle": "string"},
  "sections": [
    {
      "heading": "string",
      "body": "string",
      "cta": {"text": "string", "url_placeholder": "string"}
    }
  ],
  "closing": {"text": "string", "signature": "string"},
  "metadata": {
    "estimated_read_time": "string",
    "word_count": 0,
    "best_send_time": "string",
    "recommended_segment": "string"
  }
}
Return ONLY valid JSON, no markdown. Write engaging, conversion-focused copy."""


@app.route("/")
def home():
    return render_template_string(HOME_HTML)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    topic = data.get("topic", "")
    audience = data.get("audience", "")
    tone = data.get("tone", "professional")
    length = data.get("length", "medium")
    plan = data.get("plan", "basic")

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    length_guide = {"short": "300-400 words, 2-3 sections", "medium": "500-700 words, 3-5 sections", "long": "800-1200 words, 5-7 sections"}

    prompt = f"""Write a complete email newsletter:
- Topic: {topic}
- Target Audience: {audience}
- Tone: {tone}
- Length: {length_guide.get(length, length_guide['medium'])}

Generate engaging, conversion-focused newsletter copy."""

    try:
        msg = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        result = json.loads(msg.content[0].text)
        return jsonify({"success": True, "newsletter": result})
    except json.JSONDecodeError:
        return jsonify({"success": True, "newsletter": {"raw": msg.content[0].text}})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


HOME_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NewsletterPro AI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#0a0a0f;color:#e0e0e0;min-height:100vh}
.container{max-width:900px;margin:0 auto;padding:2rem}
h1{font-size:2.5rem;background:linear-gradient(135deg,#43e97b,#38f9d7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;margin-bottom:.5rem}
.sub{text-align:center;color:#888;margin-bottom:2rem;font-size:1.1rem}
.card{background:#14141f;border:1px solid #222;border-radius:16px;padding:2rem;margin-bottom:1.5rem}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
label{display:block;font-size:.85rem;color:#aaa;margin-bottom:.3rem}
input,select,textarea{width:100%;padding:.75rem;background:#1a1a2e;border:1px solid #333;border-radius:8px;color:#fff;font-size:1rem}
textarea{grid-column:1/-1;min-height:80px;resize:vertical}
.btn{grid-column:1/-1;padding:1rem;background:linear-gradient(135deg,#43e97b,#38f9d7);border:none;border-radius:10px;color:#0a0a0f;font-size:1.1rem;font-weight:700;cursor:pointer;transition:opacity .2s}
.btn:hover{opacity:.85}
.btn:disabled{opacity:.5;cursor:wait}
#result{display:none}
.nl-preview{background:#1a1a2e;border-radius:12px;overflow:hidden;margin-top:1rem}
.nl-header{background:linear-gradient(135deg,#43e97b22,#38f9d722);padding:2rem;text-align:center;border-bottom:1px solid #333}
.nl-header h2{font-size:1.5rem;color:#43e97b;margin-bottom:.3rem}
.nl-header p{color:#888;font-size:.95rem}
.nl-subject{background:#0f0f1a;padding:1rem 2rem;border-bottom:1px solid #222;font-size:.9rem}
.nl-subject strong{color:#43e97b}
.nl-body{padding:2rem}
.nl-section{margin-bottom:1.5rem}
.nl-section h3{color:#38f9d7;margin-bottom:.5rem;font-size:1.1rem}
.nl-section p{line-height:1.7;color:#ccc}
.nl-cta{display:inline-block;background:linear-gradient(135deg,#43e97b,#38f9d7);color:#0a0a0f;padding:.6rem 1.5rem;border-radius:8px;font-weight:700;margin-top:.75rem;text-decoration:none;font-size:.9rem}
.nl-closing{padding:1.5rem 2rem;border-top:1px solid #222;color:#888;font-style:italic}
.nl-meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:.75rem;margin-top:1.5rem}
.meta-card{background:#1a1a2e;border-radius:10px;padding:1rem;text-align:center}
.meta-card .label{font-size:.75rem;color:#888;text-transform:uppercase;letter-spacing:1px}
.meta-card .value{font-size:1rem;color:#43e97b;font-weight:600;margin-top:.3rem}
.copy-btn{background:#1a1a2e;border:1px solid #333;color:#43e97b;padding:.5rem 1rem;border-radius:8px;cursor:pointer;font-size:.85rem;margin-top:1rem}
.copy-btn:hover{background:#222}
.spinner{display:inline-block;width:20px;height:20px;border:3px solid #0003;border-top-color:#0a0a0f;border-radius:50%;animation:spin .8s linear infinite;margin-right:.5rem;vertical-align:middle}
@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:600px){.form-grid{grid-template-columns:1fr}h1{font-size:1.8rem}}
</style>
</head>
<body>
<div class="container">
<h1>NewsletterPro AI</h1>
<p class="sub">AI-powered email newsletters that convert</p>
<div class="card">
<div class="form-grid">
<div><label>Topic</label><input id="topic" placeholder="e.g. Weekly AI industry roundup"></div>
<div><label>Target Audience</label><input id="audience" placeholder="e.g. SaaS founders, tech enthusiasts"></div>
<div><label>Tone</label>
<select id="tone">
<option value="professional">Professional</option>
<option value="casual">Casual & Friendly</option>
<option value="witty">Witty & Engaging</option>
<option value="authoritative">Authoritative</option>
<option value="conversational">Conversational</option>
</select></div>
<div><label>Length</label>
<select id="length">
<option value="short">Short (2-3 min read)</option>
<option value="medium" selected>Medium (4-5 min read)</option>
<option value="long">Long (6-8 min read)</option>
</select></div>
<div><label>Plan</label>
<select id="plan">
<option value="basic">Basic - $12/mo (4/mo)</option>
<option value="pro">Pro - $29/mo (12/mo)</option>
<option value="agency">Agency - $49/mo (unlimited)</option>
</select></div>
<div></div>
<button class="btn" id="genBtn" onclick="generate()">Generate Newsletter</button>
</div>
</div>
<div id="result" class="card"></div>
</div>
<script>
async function generate(){
  const btn=document.getElementById('genBtn');const res=document.getElementById('result');
  btn.disabled=true;btn.innerHTML='<span class="spinner"></span>Generating...';res.style.display='none';
  try{
    const r=await fetch('/generate',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({topic:document.getElementById('topic').value,audience:document.getElementById('audience').value,
        tone:document.getElementById('tone').value,length:document.getElementById('length').value,
        plan:document.getElementById('plan').value})});
    const d=await r.json();
    if(d.error){res.innerHTML='<p style="color:#ff4444">'+d.error+'</p>';res.style.display='block';return;}
    const nl=d.newsletter;let h='';
    if(nl.subject_line){h+='<div class="nl-subject"><strong>Subject:</strong> '+nl.subject_line;
      if(nl.preview_text)h+=' &mdash; <span style="color:#666">'+nl.preview_text+'</span>';h+='</div>';}
    h+='<div class="nl-preview">';
    if(nl.header){h+='<div class="nl-header"><h2>'+(nl.header.title||'')+'</h2><p>'+(nl.header.subtitle||'')+'</p></div>';}
    if(nl.sections){h+='<div class="nl-body">';
      nl.sections.forEach(s=>{h+='<div class="nl-section"><h3>'+s.heading+'</h3><p>'+s.body+'</p>';
        if(s.cta)h+='<a class="nl-cta" href="#">'+s.cta.text+'</a>';h+='</div>';});h+='</div>';}
    if(nl.closing){h+='<div class="nl-closing">'+nl.closing.text;
      if(nl.closing.signature)h+='<br><strong style="color:#43e97b">'+nl.closing.signature+'</strong>';h+='</div>';}
    h+='</div>';
    if(nl.metadata){h+='<div class="nl-meta">';
      const m=nl.metadata;
      if(m.estimated_read_time)h+='<div class="meta-card"><div class="label">Read Time</div><div class="value">'+m.estimated_read_time+'</div></div>';
      if(m.word_count)h+='<div class="meta-card"><div class="label">Words</div><div class="value">'+m.word_count+'</div></div>';
      if(m.best_send_time)h+='<div class="meta-card"><div class="label">Best Send Time</div><div class="value">'+m.best_send_time+'</div></div>';
      if(m.recommended_segment)h+='<div class="meta-card"><div class="label">Segment</div><div class="value">'+m.recommended_segment+'</div></div>';
      h+='</div>';}
    if(nl.raw)h+='<pre style="white-space:pre-wrap;color:#ccc">'+nl.raw+'</pre>';
    h+='<button class="copy-btn" onclick="copyHTML()">Copy Newsletter HTML</button>';
    res.innerHTML=h;res.style.display='block';window._nlData=nl;
  }catch(e){res.innerHTML='<p style="color:#ff4444">Error: '+e.message+'</p>';res.style.display='block';
  }finally{btn.disabled=false;btn.textContent='Generate Newsletter';}
}
function copyHTML(){
  const nl=window._nlData;if(!nl)return;
  let html='<h1>'+(nl.header?.title||'')+'</h1>';
  if(nl.sections)nl.sections.forEach(s=>{html+='<h2>'+s.heading+'</h2><p>'+s.body+'</p>';if(s.cta)html+='<a href="#">'+s.cta.text+'</a>';});
  if(nl.closing)html+='<p><em>'+nl.closing.text+'</em></p>';
  navigator.clipboard.writeText(html).then(()=>{
    const b=document.querySelector('.copy-btn');b.textContent='Copied!';setTimeout(()=>b.textContent='Copy Newsletter HTML',2000);});
}
</script>
</body>
</html>"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
