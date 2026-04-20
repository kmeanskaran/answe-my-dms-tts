# Option B Recording Script

## Title
I Built a Voice Agent That Answers My DMs - In 15 Languages - From One Recording

## Positioning
This script is intentionally aligned to the current codebase:
- Streamlit app
- Ollama for text generation
- Smallest AI for voice output
- Markdown files as the knowledge base

Do not claim Atoms is implemented if you are recording from the current repo state.

## Short Hook
I get the same DM all the time:
"How do I get into ML?"

So I built a simple voice agent that replies in my style, using my knowledge base, and then speaks the answer back in multiple languages.

The fun part is the voice layer is powered by a cloned voice, so it sounds like me without me manually replying every time.

Let me show you the full build.

## Part 1 - What I Built
This is a very basic version of the system.

I have a Streamlit app where I type in a DM-style question, pick a language, generate the reply, and then convert that response into audio.

Under the hood:
- Ollama generates the text response
- My markdown files act as the knowledge base
- Smallest AI turns the response into speech using a cloned voice

So the stack is simple, but it is enough to show the full loop end to end.

## Part 2 - Show the App
This is the UI.

There is a question box here, a language selector here, and one button to generate the final audio.

I kept it intentionally minimal because I wanted to validate the flow first:
- Can I answer common DMs in my style?
- Can I ground the reply with my own advice?
- Can I generate audio in different languages from the same setup?

That is the main goal of this prototype.

## Part 3 - Show the Code
Let me quickly show the code.

In `app.py`, the app takes a question and selected language.
Then it calls the response generation function.
After that, it sends the final answer to Smallest AI TTS.

In `llm.py`, I load all the markdown files from the `data` folder.
Those files contain my views on learning ML, MLOps, interviews, and personal branding.

That context gets passed into the model so the reply sounds closer to what I would actually say in a real DM.

Then in `tts.py`, I pass the generated text, the selected language, and the voice ID into the TTS endpoint.

So overall, it is a pretty clean pipeline:
question in, grounded answer out, audio generated.

## Part 4 - Knowledge Base
The useful part here is not just text-to-speech.

The useful part is that the system is grounded on my own material.

For example, my advice is usually:
- build projects, not just collect certificates
- learn by shipping
- focus on MLOps and real systems
- write publicly and make your work visible

That is the kind of advice I get asked about all the time, so this use case is very natural for me.

## Part 5 - Demo 1 English
Let us test it with a very common DM:

"I am from a tier-3 college. Can I still get into ML?"

Now I generate the response in English.

Play the output here.

My take on the result:
the response is concise, sounds like my style, and it is already useful enough for repetitive mentorship questions.

## Part 6 - Demo 2 Hindi
Now I switch the exact same workflow to Hindi.

Same question pattern, same knowledge base, same voice pipeline, different output language.

Play the Hindi output here.

This is where it gets interesting, because now the same system can answer in a more accessible way for a wider audience.

## Part 7 - Demo 3 Marathi
Now let me try Marathi.

This is the part I personally find the most fun, because hearing your own cloned voice deliver advice in another language feels very different from a normal chatbot demo.

Play the Marathi output here.

## Part 8 - Honest Take
My honest take:

This is still a basic prototype, not a finished product.

What works:
- fast way to turn repeated DM answers into audio replies
- grounded on my own knowledge files
- multilingual output from the same interface
- simple enough to iterate on quickly

What I would improve next:
- actual DM platform integration
- better retrieval instead of loading every markdown file at once
- latency and cost tracking in the UI
- a more production-ready voice agent flow

## Closing
But even in this basic form, this is already a useful builder workflow.

Instead of answering the same question again and again manually, I can turn my advice into a reusable voice agent.

If you want to build something similar, the link is in the post.

Clone your voice, plug in your knowledge base, and build a real use case around it.

## B-Roll Prompts
- Show `app.py`
- Show `llm.py`
- Show `tts.py`
- Show `data/` markdown files
- Show one English generation
- Show one Hindi generation
- Show one Marathi generation
- Zoom into the language selector
- Zoom into the final audio player

## On-Screen Questions To Use
- How do I get into ML from scratch?
- I am from a tier-3 college. Is it over for me?
- Should I learn ML first or MLOps first?
- Are certifications worth it for getting into AI?
- How do I build projects that actually help me get hired?
