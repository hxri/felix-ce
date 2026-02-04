from src.clients.fal_client import FalClient


def main():

    client = FalClient()

    result = client.subscribe(
        "fal-ai/nano-banana",
        arguments={
            "prompt": "portrait photo of a person smiling",
            "num_images": 1,
        },
    )

    print(result)


if __name__ == "__main__":
    main()
