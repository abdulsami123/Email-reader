import vertexai
from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerationResponse,
    GenerativeModel,
    Image,
    Part,
)
import http.client
import io
import typing
import urllib.request
import IPython.display
from PIL import Image as PIL_Image
from PIL import ImageOps as PIL_ImageOps

Contents = str | list[str | Image | Part]

# Define project information
PROJECT_ID = "hopeful-sunset-411201"  # @param {type:"string"}
LOCATION = "us-central1"  # @param {type:"string"}
#Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)


def generate_content(
    model: GenerativeModel,
    contents: Contents,
    temperature: float = 0.0,
    top_p: float = 0.0,
    top_k: int = 1,
) -> list[GenerationResponse]:
    """Call the Vertex AI Gemini API.

    Default parameters have low randomness in this notebook for consistency across calls.
    """
    generation_config = GenerationConfig(
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        candidate_count=1,
        max_output_tokens=2048,
    )

    responses = model.generate_content(
        contents,
        generation_config=generation_config,
        stream=True,
    )

    # In streaming mode, multiple GenerationResponse can be generated
    # In unary (non-streaming) mode, a single GenerationResponse is returned
    return [responses] if isinstance(responses, GenerationResponse) else list(responses)


def print_contents(contents: Contents):
    """Print the full contents for ease of readability."""
    if not isinstance(contents, list):
        contents = [contents]

    print(" Contents ".center(80, "-"))
    for content in contents:
        if display_content_as_image(content):
            continue
        if display_content_as_video(content):
            continue
        print(content)


def display_content_as_image(content: str | Image | Part) -> bool:
    if not isinstance(content, Image):
        return False
    display_image(content)
    return True


def display_content_as_video(content: str | Image | Part) -> bool:
    if not isinstance(content, Part):
        return False
    part = typing.cast(Part, content)
    file_path = part.file_data.file_uri.removeprefix("gs://")
    video_url = f"https://storage.googleapis.com/{file_path}"
    IPython.display.display(IPython.display.Video(video_url, width=600))
    return True


def print_responses(responses: list[GenerationResponse], as_markdown: bool = True):
    """Print the full responses."""
    # Consolidate the text
    text = "".join(
        part.text
        for response in responses
        for part in response.candidates[0].content.parts
    )
    # Remove potential leading/trailing spaces
    text = text.strip()

    print(" Start of responses ".center(80, "-"))
    if as_markdown:
        IPython.display.display(IPython.display.Markdown(text))
    else:
        print(text)
    print(" End of responses ".center(80, "-"))
    print("")


def display_image(image: Image, max_width: int = 600, max_height: int = 350):
    pil_image = typing.cast(PIL_Image.Image, image._pil_image)
    if pil_image.mode != "RGB":
        # Modes such as RGBA are not yet supported by all Jupyter environments
        pil_image = pil_image.convert("RGB")

    image_width, image_height = pil_image.size
    if max_width < image_width or max_height < image_height:
        # Resize to display a smaller notebook image
        pil_image = PIL_ImageOps.contain(pil_image, (max_width, max_height))

    display_image_compressed(pil_image)


def display_image_compressed(pil_image: PIL_Image.Image):
    """Display the image in a compressed format to reduce the notebook size."""
    image_io = io.BytesIO()
    pil_image.save(image_io, "jpeg", quality=80, optimize=True)
    image_bytes = image_io.getvalue()
    ipython_image = IPython.display.Image(image_bytes)
    IPython.display.display(ipython_image)


def load_image_from_url(image_url: str) -> Image:
    image_bytes = get_image_bytes_from_url(image_url)
    return Image.from_bytes(image_bytes)


def get_image_bytes_from_url(image_url: str) -> bytes:
    with urllib.request.urlopen(image_url) as response:
        response = typing.cast(http.client.HTTPResponse, response)
        image_bytes = response.read()
    return image_bytes

model = GenerativeModel("gemini-pro")

contents = """
What happened to optimus prime? When?
Explain simply in one sentence.
"""
responses = generate_content(model, contents)
print_contents(contents)
print_responses(responses)