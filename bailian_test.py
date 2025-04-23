import os
from http import HTTPStatus
from dashscope import Application
import gradio as gr

def stream_rag(abstract: str, month: int):
    """
    每次 yield 完整的累积文本，Gradio 会自动在前端更新。
    """
    biz_params = {"abstract": abstract, "month": str(month)}
    responses = Application.call(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        app_id='98476d1974e44ca98066328927954f3a',
        prompt='rag',
        stream=True,
        biz_params=biz_params,
        flow_stream_mode="agent_format",
        incremental_output=True
    )

    full_text = ""
    for response in responses:
        if response.status_code != HTTPStatus.OK:
            # 出错时直接返回错误文本并结束生成
            yield f"请求失败: code={response.status_code}，message={response.message}"
            return
        chunk = response.output.text
        full_text += chunk
        # 把当前累积结果 yield 回去，前端会增量渲染
        yield full_text

# 使用 gr.Interface，回调返回生成器即可
iface = gr.Interface(
    fn=stream_rag,
    inputs=[
        gr.Textbox(lines=5, label="论文摘要", placeholder="在此输入论文摘要…"),
        gr.Number(label="期望投稿月份", value=5, precision=0, interactive=True),
    ],
    outputs=gr.Markdown(label="会议推荐结果"),
    title="会议推荐",
    description="输入论文摘要和期望月份，实时展示推荐结果。",
)

if __name__ == "__main__":
    iface.launch(share=True)
