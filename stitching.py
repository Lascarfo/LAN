import cv2
import numpy as np
import matplotlib.pyplot as plt

def getparams(image):
    f = plt.imread('{}'.format(image))
    fcv2 = f[:,:,::-1] # OpenCV uses BGR ordering of color channels
    plt.imshow(f)
    fcv2 = cv2.normalize(fcv2, None, 0, 255, cv2.NORM_MINMAX).astype('uint8')
    sift = cv2.xfeatures2d.SIFT_create()
    kps, dscs = sift.detectAndCompute(fcv2, mask=None)
    return kps, dscs, fcv2

def stitch_image(imagePaths, outputPath='./output.png'):
    features_dis = 20
    while features_dis <= 200:
        try:
            path1 = imagePaths[0]
            path2 = imagePaths[1]
            kps1, dscs1, img1 = getparams(path1)
            kps2, dscs2, img2 = getparams(path2)

            matcher = cv2.BFMatcher()
            matches = matcher.match(dscs1, dscs2)
            good = []
            for m in matches:
                # print(m.distance)
                if m.distance < features_dis:
                    good.append(m)

            # draw_params = dict(matchColor=(0, 255, 0),
            #                        singlePointColor=None,
            #                        flags=2)

            # img3 = cv2.drawMatches(img1, kps1, img2, kps2, good, None, **draw_params)
            # cv2.imwrite("./out.png", img3)
            # print(len(good))

            src_pts = np.float32([kps1[m.queryIdx].pt for m in good])
            dst_pts = np.float32([kps2[m.trainIdx].pt for m in good])
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            h, w, _ = img1.shape

            # print(dst)
            # img2 = cv2.polylines(img2,[np.int32(dst)],True,255,3, cv2.LINE_AA)
            #cv2.imshow("original_image_overlapping.jpg", img2)

            def warpTwoImages(img1, img2, H):
                h1, w1 = img1.shape[:2]
                h2, w2 = img2.shape[:2]
                pts1 = np.float32([[0, 0], [0, h1], [w1, h1], [w1, 0]]).reshape(-1, 1, 2)
                pts2 = np.float32([[0, 0], [0, h2], [w2, h2], [w2, 0]]).reshape(-1, 1, 2)
                pts2_ = cv2.perspectiveTransform(pts2, H)
                pts = np.concatenate((pts1, pts2_), axis=0)
                [xmin, ymin] = np.int32(pts.min(axis=0).ravel() - 0.5)
                [xmax, ymax] = np.int32(pts.max(axis=0).ravel() + 0.5)
                t = [-xmin, -ymin]
                Ht = np.array([[1, 0, t[0]], [0, 1, t[1]], [0, 0, 1]]) # translate

                result = cv2.warpPerspective(img2, Ht.dot(H), (xmax - xmin, ymax - ymin))
                result[t[1]:h1+t[1], t[0]:w1+t[0]] = img1
                return result

            dst = warpTwoImages(img2, img1, M)
            cv2.imwrite(outputPath, dst)

            return 0
        except:
            features_dis += 10
