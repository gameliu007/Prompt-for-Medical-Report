import json
# from rouge import Rouge
import time
import openai
import os


openai.proxy = "https://127.0.0.1:7890"
# openai.api_base = "https://127.0.0.1/v1/"
openai.api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

def get_completion(prompt, model="gpt-3.5-turbo",temperature=1.0,top_p=1.0): # Andrew mentioned that the prompt/ completion paradigm is preferable for this class
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
        top_p=top_p,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response.choices[0].message["content"]


ls_diagnosis = "小儿支气管炎、小儿发热、小儿腹泻、上呼吸道感染、小儿消化不良、小儿感冒、小儿咳嗽、新生儿黄疸、小儿便秘、小儿支气管肺炎等。"

ls_aux_test = "血常规、尿常规、粪便常规、支原体、肝功能、肾功能、凝血功能、血型鉴定、X射线、CT扫描、MRI、超声波等。"

ls_pre_history="当前的症状、发生部位、发生时间、频率、持续时间、严重程度、伴随症状、药物治疗等。"

ls_past_history= """
既往病史：患者曾经患过的疾病，如高血压、糖尿病、哮喘等。
手术史：患者曾经接受过的手术，包括手术的种类、时间和结果等。
药物过敏史：患者对某些药物或物质存在过敏反应的情况，如青霉素过敏等。
家族病史：患者的家族成员是否有某些疾病的遗传倾向或患病情况，如高血压、糖尿病、心脏病等。
"""

ls_symptom = "发热、咳嗽、喉咙痛、流鼻涕、腹痛、腹泻、喷嚏呕吐、拉肚子、肚子疼、疲倦、乏力等。"


def get_summary_prompt_T(ls_dialog, temp=0.1,top1=1.0):     # Techical Type
    prompt = f"""
    任务:根据医患对话{ls_dialog}生成一段简短的医学摘要，包含以下六个部分：
    主诉:不超过20字，包括以症状{ls_symptom}为例，根据医患对话生成症状，症状天数。
    现病史:不超过80字，生成相关的现病史,以{ls_pre_history}为例。
    辅助检查:生成最相关的医学检查名称,以{ls_aux_test}为例。
    既往史:不超过50字，生成相关的既往史,以{ls_past_history}为例。
    诊断:生成一个最相关的诊断名称,以{ls_diagnosis}为例。
    建议:不超过80字,生成所有建议。
    """
    response = get_completion(prompt,temperature=temp,top_p=top1)
    return response


def get_summary_prompt_S(ls_dialog, temp=0.1,top1=0.1):  # Simple Type
    prompt = f"""
    1.根据医疗对话{ls_dialog}生成一段简短的医学摘要.
    2.包含以下六个部分：
    主诉:
    现病史:
    辅助检查:医学检查项目名称
    既往史:
    诊断:最相关的诊断名称
    建议:
    """
    response = get_completion(prompt,temperature=temp,top_p=top1)
    return response


def write_result_in_file(write_path, write_content):
    print("开始生成文件，请稍候-------------------------------------------")
    ll_count = len(write_content)
    ll_num = 0

    with open(write_path, 'w') as f:

        for dict_content in write_content:
            for i in dict_content[0]:
                ls_utterance = ""
                for j in i:
                    ls_utterance = ls_utterance +  j
                f.writelines(ls_utterance.rstrip()+"\n\n")
            for i in dict_content[1]:
                ls_summary = ""
                for j in i:
                    ls_summary =  j
                    f.writelines(ls_summary)
                    f.writelines("\n\n")
            for i in dict_content[2]:
                for j in i:
                    ls_summary = j
                    f.writelines(ls_summary)
                    f.writelines("\n\n")
            # for i in dict_content[3]:
            #     for j in i:
            #         ls_summary = j
            #         f.writelines(ls_summary)
            #         f.writelines("\n\n")
            # for i in dict_content[4]:
            #     for j in i:
            #         ls_summary = j
            #         f.writelines(ls_summary)
            #         f.writelines("\n\n")
            # for i in dict_content[5]:
            #     for j in i:
            #         ls_summary = j
            #         f.writelines(ls_summary)
            #         f.writelines("\n\n")
            #
            # for i in dict_content[6]:
            #     for j in i:
            #         ls_summary = j
            #         f.writelines(ls_summary)
            #         f.writelines("\n\n")
            #
            # for i in dict_content[7]:
            #     for j in i:
            #         ls_summary = j
            #         f.writelines(ls_summary)
            #         f.writelines("\n\n")
            #
            # for i in dict_content[8]:
            #     for j in i:
            #         ls_summary = j
            #         f.writelines(ls_summary)
            #         f.writelines("\n\n")

            # ll_num = ll_num + 1
            # print(str((ll_num/ll_count)*100) +'%')


# 由于文件中有多行，直接读取会出现错误，因此一行一行读取
from pathlib import Path

# json_file = './data/IMCS-V2_train.json'
json_file = './data/IMCS-V2_dev.json'
# json_file = './data/IMCS-V2_test.json'
# json_log_file = './data/Log1.json'

ls_total = []

path = Path("./data/new/diag_chatgpt/")
ls_root = "./data/new/diag_chatgpt/"
all_json_file = list(path.glob('*.story'))
ll_num_1 = 0
ll_num_1 = len(all_json_file)+1

print("开始读取文件，请稍候-------------------------------------------")
with open(json_file,encoding="utf-8") as f:

    dic = json.load(f)
    ll_count = len(dic)
    ll_num = 0
    for key in dic:

        ls_totel = []
        ls_temp = []
        ls_description = []
        ls_summary0 = []
        ls_utterance = []

        ls_content = dic[key]           #开始解析详细数据


        ll_num = ll_num + 1
        if ll_num < ll_num_1 or ll_num > 500:
        # if ll_num < ll_num_1:
            continue

        #####################SUM2-start###############生成汇总2#############
        ls_report = ls_content["report"]
        li_index = 0
        for i in ls_report:  # 主诉
            ls_temp = []
            ls_temp.append("L-highlight")
            if len(i["建议"]) < 1:
                break
            ls_temp.append("主诉："+i["主诉"] + " "+ "现病史：" + i["现病史"] + " "+ "辅助检查：" + i["辅助检查"] + " " + "既往史："+ i["既往史"] + " "+"诊断："+i["诊断"]+ " " + "建议：" + i["建议"])
            # ls_temp.append(i["主诉"] + " " + i["现病史"] + " "  + i["辅助检查"] + " "  + i["诊断"] + " " + i["建议"])
            # ls_temp.append(i["建议"])
            li_index = li_index + 1
            ls_summary0.append(ls_temp)
        #####################SUM2-end###################################


        ls_temp = []
        if len(ls_content["self_report"]) < 1:
            break
        ls_temp.append('患者：')
        ls_temp.append(ls_content["self_report"])    #description--患者提问标题，可以把这段话当作一个患者的对话，且具有相当的参考作用
        ls_utterance.append(ls_temp)

        ls_dialogue = ls_content["dialogue"]

        for i in ls_dialogue:
            ls_temp = []
            ldc_Max_score = 0
            if i["speaker"] == "医生":
                s1 = "医生："
            else:
                s1 = "患者："
            ls_temp.append(s1)
            ls_sentence = i["sentence"]
            ls_temp.append(ls_sentence)
            ls_utterance.append(ls_temp)

        ls_temp = []
        ls_total= []
        ls_summary = []


        ls_dialogue_str = ''
        for i in ls_utterance:
            ls_dialogue_str = ls_dialogue_str + ' ' + ' '.join(i)

        ls_return = ''
        ls_return = get_summary_prompt_T(ls_dialogue_str, 0.1, 0.1)              # technical type
        # ls_summary = get_summary_prompt_S(ls_dialogue_str, 0.1, 0.1)           # simple type

        ls_temp = []
        ls_temp.append('highlight')
        ls_temp.append(ls_return)
        ls_summary.append(ls_temp)
        # time.sleep(1)

        # ls_summary1 = []
        # ls_cc = get_summary(ls_dialogue_str, 0.7, 1.0)
        #
        # ls_temp = []
        # ls_temp.append('highlight')
        # ls_temp.append(ls_cc)
        # ls_summary1.append(ls_temp)                      #SUM2
        # time.sleep(3)
        #
        # #  # #
        # ls_summary2 = []
        # ls_cc = get_summary(ls_dialogue_str, 1.0, 0.1)
        # ls_temp = []
        # ls_temp.append('highlight')
        # ls_temp.append(ls_cc)
        # ls_summary2.append(ls_temp)  # SUM3
        # time.sleep(3)
        # #
        # ls_summary3 = []
        # ls_cc = get_summary(ls_dialogue_str, 0.1, 1.0)
        # ls_temp = []
        # ls_temp.append('highlight')
        # ls_temp.append(ls_cc)
        # ls_summary3.append(ls_temp)  # SUM3
        # time.sleep(3)
        #
        # #
        # ls_summary4 = []
        # ls_cc = get_summary(ls_dialogue_str, 0.5, 0.5)
        # ls_temp = []
        # ls_temp.append('highlight')
        # ls_temp.append(ls_cc)
        # ls_summary4.append(ls_temp)  # SUM3
        # time.sleep(3)
        #
        # #
        # ls_summary5 = []
        # ls_cc = get_summary(ls_dialogue_str, 0.7, 0.1)
        # ls_temp = []
        # ls_temp.append('highlight')
        # ls_temp.append(ls_cc)
        # ls_summary5.append(ls_temp)  # SUM3
        # time.sleep(3)
        #
        # #
        # ls_summary6 = []
        # ls_cc = get_summary(ls_dialogue_str, 0.1, 0.1)
        # ls_temp = []
        # ls_temp.append('highlight')
        # ls_temp.append(ls_cc)
        # ls_summary6.append(ls_temp)  # SUM3
        # time.sleep(3)


        ls_temp = []
        ls_temp.append(ls_utterance)
        ls_temp.append(ls_summary0)        # orginal summary in dialog
        ls_temp.append(ls_summary)         # summary generation by chatgpt  SUM1+SUM2+sum3
        # ls_temp.append(ls_summary1)
        # ls_temp.append(ls_summary2)
        # ls_temp.append(ls_summary3)
        # ls_temp.append(ls_summary4)
        # ls_temp.append(ls_summary5)
        # ls_temp.append(ls_summary6)
        ls_total.append(ls_temp)

        write_result_in_file(ls_root+'valid'+str(ll_num)+'.story',ls_total)

        # write_result_in_file(ls_root + 'valid' + str(ll_num) + '.story', ls_total)
        # write_result_in_file(ls_root + 'test' + str(ll_num) + '.story', ls_total)
        print(str((ll_num / ll_count) * 100) + '%')


