_PPTX_TEMPLATE_LOCATION = "../resources/PromptsDeck.pptx"
_PPTX_ONE_SHOT_LOCATION = "../resources/ZeroShotExampleDeck.pptx"
PPTX_OUTPUT_LOCATION = "../resources/OutputDeck.pptx"
_TXT_INPUT_LOCATION = "../resources/Context.txt"
DEFAULT_SYSTEM_PROMPT = ("You are a business development manager. Your primary job is to take the text you read and "
                         "re-word it, summarize it, and generally modify it to address particular business outcomes. "
                         "In the absence of concrete business outcomes, adhere to a default tone and diction fitting "
                         "a business-professional context. Keep responses simple and unstructured, avoiding common "
                         "templates like e-mail or instant message. Where possible, lean on the output format "
                         "specified in the prompt. Absent this, keep responses short, not to exceed the word count "
                         "in the instruction. It is perfectly acceptable to respond with the unaltered prompt where "
                         "appropriate. Put your explanation within the <rationale/> XML tags. Put your response in "
                         "the <response> XML tags."
                         "You can expect prompts to have the following elements: INPUT DATA, CONTEXT, and OUTPUT "
                         "FORMAT. The input data is what you're being asked to do. The context is background "
                         "information on the customer or scenario you're performing this task for; the context "
                         "contains many important pieces of information for contextualizing your responses. The "
                         "output format describes how the output should be formatted.")
DEFAULT_OUTPUT_INDICATOR = ("Output should be succinct and maintain a business-professional tone. Limit to between "
                            "10 - 50 words. Avoid run-on sentences, but combine ideas to reduce the number of "
                            "paragraphs.")

SYSTEM_PROMPT_PATTERN = r"<SYSTEM>(.*)</SYSTEM>"
GENERATE_PROMPT_PATTERN = r"<GENERATE>(.*)</GENERATE>"
GENERATE_CHART_PROMPT_PATTERN = r"<GENERATE_CHART>(.*)</GENERATE_CHART>"
OUTPUT_PROMPT_PATTERN = r"<FORMAT>(.*)</FORMAT>"
# Default max number of threads not exceeding Bedrock service quota:
# https://docs.aws.amazon.com/bedrock/latest/userguide/quotas.html
MAX_NUM_THREADS = 45
CONFIG_FILE_NAME = "bisheng.yaml"
