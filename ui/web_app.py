import gradio as gr
from pybehaviac.tree_nl import *


def step(file_obj, ):
    pass


def run():
    with gr.Blocks(
        title='Behaviac Editor',
        theme=gr.themes.Soft()
    ) as demo:
        gr.HTML("""<h1 align="center">Behaviac LM Editor</h1>""")
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""<b align="center">Upload XML file to be modified</b>""")
                o_file = gr.File(
                    value='/home/zx/projs/llm_bt/derk_bt/behaviac_xml/fighter.xml',
                    file_count='single',
                    file_types=['.xml'],
                    interactive=True,
                    type='file',
                    label='',
                    show_label=False
                )
            with gr.Column(scale=8):
                chatbot = gr.Chatbot(
                    show_label=False,
                    height=700
                )

                input_box = gr.Textbox(
                    show_label=False,
                    placeholder='Input new requirement here, press ENTER to send...',
                )
            with gr.Column(scale=1):
                temp_sld = gr.Slider(
                    minimum=0,
                    maximum=1,
                    value=0.5,
                    step=0.05,
                    label='Temperature',
                    interactive=True
                )
        input_box.submit(
            step,
            [o_file, input_box, chatbot],
            []
        )
    demo.queue(concurrency_count=1)
    demo.launch(share=False, server_name='0.0.0.0', server_port=1357)

if __name__ == '__main__':
    run()
