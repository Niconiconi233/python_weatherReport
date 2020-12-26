#from weather import Weather 
import os

def main():
    # weather = Weather()
    # weather.work()
    dir = os.environ
    print(dir.get('APP_KEY'))


if __name__ == '__main__':
    main()
