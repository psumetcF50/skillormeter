from src.agent import create_agent, SkillRecommenderModel




if __name__=="__main__":

    system_prompt = """

You are an expert in human resources, industrial psychology, and talent management, specializing in job skills analysis and ranking.

I need your help to extract or infer, and evaluate skills based on a given input.


---
**Final Output Format**

Return only a JSON object:

```json
{
  "skills": [<skill name>-<proficiency>, ...],
}
```
"""

    user_prompt = f"""
            Python developer which writes advances scripts
            """

    agent = create_agent(system_prompt)

    input_data = {"input_params":user_prompt}
    result:SkillRecommenderModel = agent.invoke(input=input_data)

    print(result)