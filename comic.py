import streamlit as st
from langchain import LLMChain
from langchain.prompts.prompt import PromptTemplate
from typing import Any, Dict
from pydantic import Extra, root_validator
from langchain.llms.base import LLM
from langchain.utils import get_from_dict_or_env
import json
from langchain.chat_models import ChatOpenAI
from typing import Union, List, Dict, Any
import openai
from sdxl import fetch_data_from_hf, save_image_from_asset_url
import base64

PAGE_CONFIG = {"page_title":"Graphic Novel Garage", 
               "layout":"centered", 
               "initial_sidebar_state":"auto",
                "page_icon":"💬",
               }

st.set_page_config(**PAGE_CONFIG)

def strict_output(system_prompt: str,user_prompt: Union[str, List[str]],output_format: Dict[str, Any], default_category: str = "",output_value_only: bool = False,num_tries: int = 1,verbose: bool = False) -> Any:


    list_input = isinstance(user_prompt, list)
    dynamic_elements = any('<' in str(val) and '>' in str(val) for val in output_format.values())
    list_output = any('[' in str(val) and ']' in str(val) for val in output_format.values())
    
    error_msg = ""

    for i in range(num_tries):
        output_format_prompt = f"\nYou are to output {'an array of objects in' if list_output else ''} the following in json format: {json.dumps(output_format)}. \nDo not put quotation marks or escape character \\ in the output fields."

        if list_output:
            output_format_prompt += "\nIf output field is a list, classify output into the best element of the list."

        if dynamic_elements:
            output_format_prompt += "\nAny text enclosed by < and > indicates you must generate content to replace it. Example input: Go to <location>, Example output: Go to the garden\nAny output key containing < and > indicates you must generate the key name to replace it. Example input: {'<location>': 'description of location'}, Example output: {school: a place for education}"

        if list_input:
            output_format_prompt += "\nGenerate an array of json, one json for each input element."

        #p_template = ''' 
        #                {system_prompt} + '\n' + {output_format_prompt} + '\n' + {user_prompt}
#
        #            '''
        #llm = TogetherLLM(
        #        model= "togethercomputer/llama-2-7b-chat",
        #        temperature = 0.7,
        #        max_tokens = 1024
        #    )
        #
        #qa = LLMChain(
        #    llm=ChatOpenAI(temperature=0.7,model='gpt-3.5-turbo',openai_api_key='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'),
        #    prompt= PromptTemplate(template=p_template, input_variables=['system_prompt','output_format_prompt','user_prompt'])
        #)
#
        #res = qa({'system_prompt': system_prompt, 'output_format_prompt': output_value_only, 'user_prompt': str(user_prompt)})['text']
        #print(res)

        openai.api_key ='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'

        conversation = [
            {"role": "system", "content": f"{system_prompt}{output_format_prompt}{error_msg}"},
            {"role": "user", "content": str(user_prompt)}
        ]
        
        # Get OpenAI response
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=conversation,
            temperature=0.7,
        )

        res = response['choices'][0]['message']['content']
        res = res.replace(r"(\w)\"(\w)", r"\1'\2")

        try:
            output = json.loads(res)

            if list_input:
                if not isinstance(output, list):
                    raise ValueError("Output format not in an array of json")
            else:
                output = [output]

            for index in range(len(output)):
                for key in output_format.keys():
                    if "<" in key and ">" in key:
                        continue
                    if key not in output[index]:
                        raise ValueError(f"{key} not in json output")
                    
                    if isinstance(output_format[key], list):
                        choices = output_format[key]
                        if isinstance(output[index][key], list):
                            output[index][key] = output[index][key][0]
                        if output[index][key] not in choices and default_category:
                            output[index][key] = default_category
                        if ":" in output[index][key]:
                            output[index][key] = output[index][key].split(":")[0]

                if output_value_only:
                    output[index] = list(output[index].values())
                    if len(output[index]) == 1:
                        output[index] = output[index][0]

            return output if list_input else output[0]

        except Exception as e:
            error_msg = f"\n\nResult: {res}\n\nError message: {e}"
            print("An exception occurred:", e)
            print('\n\n')
            print("Current invalid json format", res)

    return []


def main():

    st.markdown("<h1 style='text-align: center; font-family: Arial;'>💬</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-family: italic;'><span style='color: #6f42c1;'>Graphic Novel Garage</span></h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; font-family: Courier New;'><span style='background: linear-gradient(to right, #007BFF, #28a745); -webkit-background-clip: text; color: transparent;'>Weave Stories into Comics with AI </span></h4>", unsafe_allow_html=True)
    st.markdown('<br>' * 2, unsafe_allow_html=True)

    with st.form('my_form'):
        user_input = st.text_input("Enter the story that you want to get comic from.", value = '')
        submit_button = st.form_submit_button(label='Generate Comic')
        if submit_button:
            if user_input != '':
                print("got user input")
                print("Engaging AI to generate instructions...")
                res = strict_output(
                    "You are a comic book author specialized in creating drawing instructions and captions for silent comic books based on the user given story.Make sure to generate correct words with correct spellings .Store all the variables provided in a JSON array. Always maintain the character consistency in the story and in instructions.You should always maintain a character consistency in all the 4 panels. The story should be coherent and consistent. The drawing instructions about any character in the story should be consistent in all the 4 panels. The captions should be consistent in all the 4 panels",
                    f"You are to generate a comic book page with 4 panels with the drawing instructions and captions about the following story: {user_input}. You should always maintain a character consistency in all the 4 panels. The story should be coherent and consistent. The drawing instructions about any character in the story should be consistent in all the 4 panels. The captions should be consistent in all the 4 panels. Write a drawing instructions that looks like a professional comic book artist wrote it. Write drawing instructions in a way that visuals should be beautiful and awesome",

                    {   
                        "Title": "Title of the comic book page",
                        "panel1": "drawing instructions for panel 1",
                        "caption1": "caption for panel 1",
                        "panel2": "drawing instructions for panel 2",
                        "caption2": "caption for panel 2",
                        "panel3": "drawing instructions for panel 3",
                        "caption3": "caption for panel 3",
                        "panel4": "drawing instructions for panel 4",
                        "caption4": "caption for panel 4"
                    }
                )

                if res:
                    print("got instructions for comic")
                    print("Engaging AI to generate comic...")
                    prompt = [f"Instructions: {res['panel1']}", f"Instructions: {res['panel2']}", f"Instructions: {res['panel3']}", f"Instructions: {res['panel4']}"]
                    model = 'stabilityai/stable-diffusion-xl-base-1.0'
                    images = []
                    try:
                        for i in prompt:
                            blob, content_type = fetch_data_from_hf(i, model)
                            asset_url = f"data:{content_type};base64,{base64.b64encode(blob).decode('utf-8')}"
                            img = save_image_from_asset_url(asset_url)
                            images.append(img)
                        st.markdown("<h4 style='text-align: center; font-family: Courier New;'><span style='background: linear-gradient(to right, #8C1AFF, #FF8F00); -webkit-background-clip: text; color: transparent;'> Title: {} </span></h4>".format(res['Title']), unsafe_allow_html=True)
                        st.image(images, caption=[res['caption1'], res['caption2'], res['caption3'], res['caption4']], use_column_width='auto', clamp=True)
                        print("Job done!")


                    except ConnectionError as ce:
                        print(ce)
                    except Exception as e:
                        print(f"An unexpected error occurred: {str(e)}")
            else:
                st.error('Please enter a story.')
            


if __name__ == "__main__":
    main()
