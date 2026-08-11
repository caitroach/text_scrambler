# text_scrambler
You may have heard that Anthropic is introducing undetectable "watermarks" into all outputs, at the model level. The watermark is invisible, does not change meaning or quality, and can survive copy-pasting, editing, reformatting, and even re-typing. This is not, as I originally thought, due to the insertion of invisible Unicode characters ([which are really easy to find with free online tools](https://www.soscisurvey.de/tools/view-chars.php)) into output text. 

<img width="1039" height="365" alt="image" src="https://github.com/user-attachments/assets/d13979bc-8990-4712-92c6-f3b06d9e485a" />

So how does it really work? Math!

Although they haven't directly disclosed how they're actually doing this, Anthropic is probably using a method called **statistical watermarking**, where, instead of embedding a clearly defined watermark into text or audio/visual content, models embed secret statistical patterns within the content while it's being generated. For the purpose of this repo, I'm only considering text. 

LLMs are non-deterministic; the same prompt can result in a near-infinite number of possible responses, even when the model and environment remain unchanged. Why? 

Any language model generates text one token (a short word, part of a word, number, etc) at a time. At each step, the model assigns a score to every candidate token, which are transformed into probabilities of which token comes next. The selected token is added to the context and the model calculates a new set of scores for the next token.

For instance, take the incomplete sentence *Cait goes*. An LLM forms predictions about the likelihood of the next token in the sentence. It might assign probability 0.7 to "to", 0.15 to "from", 0.10 to "away", and 0.05 to all other candidates combined. 

However, LLMs don't just pick the token with the highest probability score; that'd make them sound dull and repetitive. Instead, randomness is introduced through temperature, which scales the probability distribution of the next predicted token before selection. Low values (0.0-0.3) produce deterministic responses, while high values (0.7 and up) produce unpredictability. 

<img alt="image" src="https://github.com/user-attachments/assets/5c1accf2-3e9f-4db8-a3a1-ea77255f260d" />
<img alt="image" src="https://github.com/user-attachments/assets/115ed244-5115-46f0-871f-222fd592b086" />

*images via (Daily Dose of Data Science)[https://www.dailydoseofds.com/p/what-is-temperature-in-llms/]*

Temperature is used in a mathematical formula that determines the next token: 
<img alt="image" src="https://github.com/user-attachments/assets/1cc2aeb4-7b98-4a66-bfa1-35fb7444543e" />
*image via (Coqueret et. al., 2026)[https://arxiv.org/pdf/2607.24372]*
