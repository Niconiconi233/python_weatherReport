from weather import Weather 
import os

def main():
    weather = Weather()
    weather.work()


if __name__ == '__main__':
    dir = os.environ
    print(dir)
    # main()