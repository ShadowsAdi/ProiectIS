import json
from .models import Post, NLPAnalysisLog
from .ollama_bridge import analyze

def moderate_post(post_id, comment_id, target_type):
    post = Post.objects.get(pk=post_id)
    result = analyze(post.content,post.files,post.images)

    data = json.loads(result["response"])
    is_toxic = data["toxicity"].lower() == "toxic"

    NLPAnalysisLog.objects.create(
        post_id=post_id,
        target_type=target_type,
        is_toxic=is_toxic,
        comment_id=comment_id,
        result=data
    )

    return is_toxic
