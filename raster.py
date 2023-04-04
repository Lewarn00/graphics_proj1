import numpy as np
from utils import *

'''
### Testing
from PIL import Image

def read_png_file(path):
    image = Image.open(path)
    image_array = np.array(image) / 255.0

    return image_array
'''

class Rasterizer():

    def __init__(self):
        self.svg_to_image_x = None
        self.svg_to_image_y = None
        self.image_to_svg_x = None
        self.image_to_svg_y = None

    def svg_to_image(self,svg, im_w, im_h):
        width_ratio = im_w / svg.w
        height_ratio = im_h / svg.h 
        return [width_ratio, height_ratio]

    def image_to_svg(self,svg, im_w, im_h):
        width_ratio = svg.w / im_w
        height_ratio = svg.h / im_h
        return [width_ratio, height_ratio]

    def point_in_line_segment(self, p, p1, p2):
        #vector from p1 to p
        v1 = (p[0] - p1[0], p[1] - p1[1])
        #vector from p1 to p2
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        #use the dot product to determine whether the point falls between the two endpoints
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        if dot_product < 0 or dot_product > (v2[0] ** 2 + v2[1] ** 2):
            #inside
            return False
        #outside
        return True

    def get_coverage_for_pixel(self,shape,x,y):
        p = [x,y]

        if shape.type == "triangle":
            p1 = shape.pts[0]
            p2 = shape.pts[1]
            p3 = shape.pts[2]
            #to see if in triangle:
            #calculate areas of the three triangles made by p and all possible pairs from (p1,p2,p3)
            #if those areas sum to a number very close to the area of the triangle
            #then the point lies inside
            area = 0.5 * abs((p2[0]-p1[0])*(p3[1]-p1[1]) - (p3[0]-p1[0])*(p2[1]-p1[1]))
            tri1 = 0.5 * abs((p1[0]-p[0])*(p2[1]-p[1]) - (p2[0]-p[0])*(p1[1]-p[1]))
            tri2 = 0.5 * abs((p2[0]-p[0])*(p3[1]-p[1]) - (p3[0]-p[0])*(p2[1]-p[1]))
            tri3 = 0.5 * abs((p3[0]-p[0])*(p1[1]-p[1]) - (p1[0]-p[0])*(p3[1]-p[1]))

            if abs(area - (tri1 + tri2 + tri3)) < 0.000001:
                return 1
            else:
                return 0
            
        if shape.type == "line":
            p2 = shape.pts[1]
            p1 = shape.pts[0]
            w = shape.width
            #calculate slope and intercept
            m = (p2[1] - p1[1]) / (p2[0] - p1[0])
            b = p1[1] - m * p1[0]
            #use distance formula to find if point falls within correct width of line
            distance = abs((p[1] - m * p[0] - b) / np.sqrt(1 + m**2))
            #if close enough to line and within line segment (point falls between the endpoints) then it lies inside
            if distance <= w/2 and self.point_in_line_segment(p, p1, p2):
                return 1
            else:
                return 0

        if shape.type == "circle":
            p0 = shape.center
            r = shape.radius
            #distance formula to calculate distance to center of circle
            distance = np.sqrt((p[0] - p0[0])**2 + (p[1] - p0[1])**2)
            #compare distance to radius
            if distance <= r:
                return 1
            else:
                return 0

    def get_bounding_box(self,shape):

        if shape.type == "triangle":
            p1 = shape.pts[0]
            p2 = shape.pts[1]
            p3 = shape.pts[2]
            #bounding box for triangle using mins and max
            #loop from min x,y to max
            min_x = min(p1[0], p2[0], p3[0])
            max_x = max(p1[0], p2[0], p3[0])
            min_y = min(p1[1], p2[1], p3[1])
            max_y = max(p1[1], p2[1], p3[1])

            return [min_x, max_x, min_y, max_y]

        if shape.type == "line":
            #this bounding box has been frustrating, so i'm making it rough
            #I'm subtracting the width from the x cord. of the leftmost point
            #and the width from the y cord. of the lower point. 
            #That gives me a min x and y. 
            p1 = shape.pts[0]
            p2 = shape.pts[1]
            width = shape.width
            x_cord = 0
            y_cord = 0
            if p1[0] <= p2[0]:
                x_cord = p1[0] - width
                if p1[1] <= p2[1]:
                    y_cord = p1[1] - width
                elif p1[1] > p2[1]:
                    y_cord = p2[1] - width
            elif p1[0] > p2[0]:
                x_cord = p2[0] - width
                if p1[1] <= p2[1]:
                    y_cord = p1[1] - width
                elif p1[1] > p2[1]:
                    y_cord = p2[1] - width

            #The max x and y I calculated by adding the min to the height and 
            #length of the line respectivelty. Then I added 2 * width. 
            #This makes for a nice sized box.
            x_distance = abs(p2[0] - p1[0]) + 2 * width 
            y_distance = abs(p2[1] - p1[1]) + 2 * width 
            #^^ seems good enough

            return [x_cord, x_cord+x_distance,y_cord,  y_cord+y_distance]


        if shape.type == "circle":
            center =  shape.center
            r = shape.radius
            #to get the min x,y and max for bounding box for circle:
            min_x = center[0] - r
            max_x = center[0] + r
            min_y = center[1] - r
            max_y = center[1] + r

            return [min_x, max_x, min_y, max_y]

    def compare_images(self, image1, image2):
        num_differ_pixels = np.sum(image1 != image2)
        percent_differ_pixels = (num_differ_pixels / image1.size) * 100
        
        return percent_differ_pixels

    def rasterize(self,svg_file,im_w,im_h,output_file=None,background=(1.0,1.0,1.0),antialias=True):
        """
        :param svg_file: file
        :param im_w: width of image to be rasterized
        :param im_h: height of image to be rasterized
        :param output_file: optional path to save numpy array
        :param background: optional background color
        :return: a numpy array of dimension (H,W,3) with values in [0.0,1.0]
        """

        background = np.array(background)
        shapes = read_svg(svg_file)
        img = np.zeros((im_h, im_w, 3))
        img[:, :, :] = background
        #get svg
        svg = shapes[0]
        #set up conversion ratios
        self.image_to_svg_x, self.image_to_svg_y = self.image_to_svg(svg,im_w, im_h)
        self.svg_to_image_x, self.svg_to_image_y = self.svg_to_image(svg,im_w, im_h)
        #loop through shapes
        for shape in shapes[1:]:
            #get bounding box for shape
            bbox = self.get_bounding_box(shape)
            #convert from svg space to image space, then floor and ceil box values as needed
            min_x, max_x, min_y, max_y = np.floor(self.svg_to_image_x * bbox[0]), np.ceil(self.svg_to_image_x * bbox[1]), np.floor(self.svg_to_image_y * bbox[2]), np.ceil(self.svg_to_image_y * bbox[3]) 
            #edge cases
            if min_x <= 0:
                min_x = 0
            if max_x >= im_w:
                max_x = im_w
            if min_y <= 0:
                min_y = 0
            if max_y >= im_h:
                max_y = im_h 
            #loop through bounding box
            for x in range(int(min_x), int(max_x)):  #range(im_w):
                for y in range(int(min_y), int(max_y)): #range(im_h):
                    if antialias == False:
                        #simple midpoint
                        pixel_centerpoint = (x+0.5,y+0.5)
                        #convert to svg
                        pixel_in_svg_x = self.image_to_svg_x * pixel_centerpoint[0]
                        pixel_in_svg_y = self.image_to_svg_y * pixel_centerpoint[1]
                        #in svg space, see if pixel is covered
                        a = self.get_coverage_for_pixel(shape,pixel_in_svg_x,pixel_in_svg_y)
                        #apply to image 
                        img[x,y] = (1-a)*img[x,y]+shape.color*a
                    else:
                        #3x3 grid
                        pixel_supersampled = [(x,y),(x+1/2,y),(x+1,y),
                                              (x,y+1/2),(x+1/2,y+1/2),(x+1,y+1/2),
                                              (x,y+1),(x+1/2,y+1),(x+1,y+1)]
                        #convert xs to svg                      
                        pixel_supersampled = [[(self.image_to_svg_x * p[0]), p[1]] for p in pixel_supersampled]
                        #convert ys to svg
                        pixel_supersampled = [[p[0],(self.image_to_svg_y* p[1])] for p in pixel_supersampled]
                        coverage = 0
                        #in svg space, see how much pixel is covered
                        for pixel in pixel_supersampled:
                            a = self.get_coverage_for_pixel(shape,pixel[0],pixel[1])   
                            coverage = coverage + a
                        #determine coverage
                        coverage = coverage / 9
                        #apply to image 
                        img[x,y] = (1-coverage)*img[x,y]+shape.color*coverage

        #need to swap axis
        img = np.swapaxes(img,1,0)

        if output_file:
            save_image(output_file, img)
            '''
            ### Testing

            pre = 'output/'
            primary = svg_file.split('/')[1].split('.')[0] 
            true_name = pre + primary + '_' + str(im_w) + '_' + str(im_h)
            if antialias:
                true_name = true_name + '_aa'
            else:
                true_name = true_name + '_noaa'
            if int(primary.split('test')[1])>4:
                true_name = true_name + '_gt'
            true_name = true_name + '.png'
            true_array = read_png_file(true_name)
            #new_array = read_png_file(output_file)
            print(self.compare_images(true_array,img))
            '''

        return img

if  __name__ == "__main__":
    Rasterizer().rasterize("tests/test6.svg",512,512,output_file="your_output.png",antialias=False)
