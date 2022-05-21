import os
from os import path
import cv2
import pafy
import time
import pytesseract
from PIL import Image, ImageOps, ImageFilter
from youtubesearchpython import *


def img_to_text(img, colorize, color1="", color2=""):

    cv2.namedWindow("Current picture", cv2.WINDOW_NORMAL)  
    imS = cv2.resize(img, (1600, 900)) # Resize image
    cv2.imshow("Current picture", imS) # Show image
    cv2.waitKey(10)  
    
    cropped = get_corner(img) #Get the corner of the picture only to search for text
    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB) #Color transformation needed from CV2 to PIL format
    cropped = Image.fromarray(cropped) #Conversion from CV2 to PIL
    #cropped.show()

    if colorize == 1:
        image = cropped.convert("L")
        image = ImageOps.colorize(image, black =color1, white =color2)

    #image = image.filter(ImageFilter.FIND_EDGES)
    #image.show()

    text_in_pic = pytesseract.image_to_string(cropped).replace('\n', '')
    return text_in_pic

def get_corner(img): #returns the feed of the gameplay image | arguement should be a cv2 format picture
    y = int(img.shape[1::-1][1]/2)
    x = int(img.shape[1::-1][0]/2 + (img.shape[1::-1][0]/2)/3)
    crop_img = img[0:y, x:img.shape[1::-1][0]]
    return crop_img

def check_YT_video(element, tag, frames_to_skip):

    start_time = time.time()
    url = element["link"]
    video_name = element["title"]

    line_counter = 0
    found_counter = 0
    frames_counter = 1
    video = pafy.new(url)
    best  = video.getbest(preftype="mp4")
    capture = cv2.VideoCapture(best.url)

    print("- Title:", element["title"], "\n- Channel:", element["channel"]["name"], "\n- Date:", element["publishedTime"], "\n- Link:", element["link"], "\n- Duration:", element["duration"], "\n- Views:", element["viewCount"]["text"])

    if element["channel"]["name"] not in banlist:

        #Check if the video check is in the dataset
        with open("dataset", "r+") as dataset:
            for line in dataset:
                if url in str(line):
                    print("Video already checked\n")
                    dataset.close()
                    return

            for line in dataset:
                if line != "\n":
                    line_counter += 1     

            dataset.write("\n" + video_name.encode('unicode-escape').decode('ASCII') + "\n" + url)
            dataset.close()


        while True:
            check, frame = capture.read()

            if frames_counter%frames_to_skip == 0:
                
                try:
                    print("----------- Trying to access frame #", frames_counter)
                    text = img_to_text(frame, 0)

                    #print(tag.lower(), "\n", text.lower())
                    #os.system("pause")

                    if tag.lower() in text.lower():
                        
                        # Display the last frame found that contains the character
                        """
                        cv2.namedWindow(tag + " in " + url, cv2.WINDOW_NORMAL)  
                        cv2.imshow(tag + " in " + video_name, frame)
                        cv2.waitKey(100)
                        """
                        
                        # Create a folder that has the video title as name and contains the frames found in the video
                        path = output_directory + "/" + video_name + "frameskip=" + str(frames_to_skip) + "_" + str(line_counter)

                        try:
                            os.mkdir(path)
                        except:
                            pass

                        cv2.imwrite(path + "/" + "frame" + str(frames_counter) + ".png", frame)
                        found_counter +=1

                except Exception as e:
                    print("Access failed.\nEnd.")
                    break
                    

            frames_counter+=1

        capture.release()
        cv2.destroyAllWindows()

        print("Number of frames containing", tag, "in this video:", found_counter)
        print("--- %s seconds ---\n" % (time.time() - start_time))

    else:
        print("User banned")


output_directory = "./outputs/"
keyword = "Faide apex"
banlist = ["Wisethug", "lyr1c"]

customSearch = CustomSearch(keyword, VideoSortOrder.relevance , limit = 100)

def main():
    try:
        while True:

            for element in customSearch.result()["result"]:
                os.system("pip install -U youtube-dl")
                os.system("pip install -U pafy")
                check_YT_video(element, "Mash", frames_to_skip = 120)  

            customSearch.next()
    except:
        main()


main()


faide = "https://youtu.be/qOn5Hzo6EIc"
