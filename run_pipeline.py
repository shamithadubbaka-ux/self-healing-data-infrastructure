from core.pipeline import SelfHealingPipeline


def main():

    pipeline = SelfHealingPipeline()

    result = pipeline.run(
        rows=500,
        introduce_errors=True,
    )

    print()
    print("=" * 60)
    print("SELF-HEALING DATA INFRASTRUCTURE")
    print("=" * 60)

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )

    print("=" * 60)


if __name__ == "__main__":
    main()