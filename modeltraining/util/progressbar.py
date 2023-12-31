def progress_bar(label: str, ratio: float):
    print("\033[0;31m" + label + ":")
    scaled = int(ratio * 100)
    print("\033[0;37m[" + "\033[0;34m=" * scaled + " " * (100 - scaled) + f"\033[0;37m] {label} is {scaled}% complete\033[2A")