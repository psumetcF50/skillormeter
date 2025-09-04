from src.agent import create_agent, SkillRecommenderModel
from src.repo_scrap.scrap_files import load_chunked_data, save_chunked_data

DATA_FILE_PATH = "git_chunked_data.json"
PROCESSED_DATA_FILE_PATH = "git_chunked_data_processed.json"
FINAL_DATA_FILE_PATH = "git_chunked_data_final.json"

SYSTEM_PROMPT = """

You are an expert in human resources, industrial psychology, and talent management, specializing in job skills analysis and ranking.

I need your help to extract or infer, and evaluate skills based on a given input.
The input comes from git repository and contain code base. Analyse the code structure and decide on skill required to write the code, and proficiency level based on code complexity.
There are three skproficiency levels:
Basic, Intermediate, Advaced 

---
**Final Output Format**

Return only a JSON object:

```json
{
  "skills": [<skill name>-<proficiency>, ...],
}
```
"""

def run_llm():
    agent = create_agent(SYSTEM_PROMPT)
    chunked_data = load_chunked_data(DATA_FILE_PATH)
    chunked_data_processed = []
    for data in chunked_data:
        user_prompt = f"""
            file_type: {data["file_type"]}\n\n
            git_changes: {data["chunk"]}
            """
        input_data = {"input_params":user_prompt}
        result:SkillRecommenderModel = agent.invoke(input=input_data)
        if result:
            data["skills"] = result[0].skills
        else:
            data["skills"]=[]
        chunked_data_processed.append(data)

    save_chunked_data(chunked_data_processed,PROCESSED_DATA_FILE_PATH)

def postprocess():
    chunked_data = load_chunked_data(PROCESSED_DATA_FILE_PATH)
    levels = ["Basic", "Intermediate", "Advaced"]
    skills_with_levels = {}
    for chunk in chunked_data:
        if chunk["author"] not in skills_with_levels:
            skills_with_levels[chunk["author"]] = {}
            
        author_skills_with_levels =  skills_with_levels[chunk["author"]]   
        all_skills = chunk["skills"]

        for skill_text in all_skills:
            if '-' not in skill_text:
                continue
            skill, level = skill_text.rsplit('-', 1)
            skill =  skill.strip()
            level = level.strip()
            if level not in levels:
                continue
            if skill not in author_skills_with_levels:
                author_skills_with_levels[skill] = level
            elif author_skills_with_levels[skill] != level:
                if author_skills_with_levels[skill] == "Basic":
                    author_skills_with_levels[skill] = level 
                elif author_skills_with_levels[skill] == "Intermediate" and level == "Advaced":
                    author_skills_with_levels[skill] = level 
        skills_with_levels[chunk["author"]] = author_skills_with_levels 
    save_chunked_data(skills_with_levels,FINAL_DATA_FILE_PATH)



if __name__=="__main__":


    #run_llm()

    postprocess()
    print("done")