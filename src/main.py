from bisheng.utils.exceptions import PrintFailureError
from bisheng.runner import Runner


def main():
    try:
        runner = Runner.load("/Users/frgud/PycharmProjects/bisheng/demo/gaab/",
                                config_file="bisheng.yaml")
        # runner = Runner.load_config("/Users/frgud/PycharmProjects/bisheng/resources/vchc/",
        #                             config_file="bisheng.yaml")

        runner.run(num_threads=1, verbose=True)
    except PrintFailureError:
        exit(1)


if __name__ == '__main__':
    main()
