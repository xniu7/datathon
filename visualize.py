import csv
from BeautifulSoup import BeautifulSoup

# this file was produced hacking on the tutorial from flowingdata found here: http://flowingdata.com/2009/11/12/how-to-make-a-us-county-thematic-map-using-free-tools/
# author: alex schultz www.alexschultz.co.uk email: alex.schultz@cantab.net

countrycodes_3_to_2 = {}


reader = csv.reader(open('country_code_2to3.csv'), delimiter=",")
for row in reader:
    try:
        countrycodes_3_to_2[row[1].strip().lower()] = row[0].strip().lower()
    except:
        pass

# Read in growth rates
penetration = {}
reader = csv.reader(open('country_scores.csv'), delimiter=",")
for row in reader:
    try:
        penetration[countrycodes_3_to_2[row[0].lower()]] = float( row[1].strip() )
    except:
        pass

# Load the SVG map
svg = open('countries.svg', 'r').read()

# Load into Beautiful Soup
soup = BeautifulSoup(svg, selfClosingTags=['defs','sodipodi:namedview','path'])

# Map colors which come from http://colorbrewer2.org/
# pink from flowingdata tutorial: colors = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"]
colors = ["#C6DBEF", "#9ECAE1", "#6BAED6", "#4292C6", "#2171B5", "#084594"] # blue

# Find counties with multiple polygons
gs = soup.contents[2].findAll('g',recursive=False)
# Find countries without multiple polygons
paths = soup.contents[2].findAll('path',recursive=False)

# define what each path style should be as a base (with color fill added at the end)
path_style = "fill-opacity:1;stroke:#ffffff;stroke-width:0.99986994;stroke-miterlimit:3.97446823;stroke-dasharray:none;stroke-opacity:1;fill:"

# replace the style with the color fill you want
for p in paths:
     if 'land' in p['class']:
        try:
            rate = penetration[p['id']]
        except:
            continue

        if rate > 90:
            color_class = 5
        elif rate > 75:
            color_class = 4
        elif rate > 60:
            color_class = 3
        elif rate > 45:
            color_class = 2
        elif rate > 30:
            color_class = 1
        else:
            color_class = 0

        # set the color we are going to use and then update the style
        color = colors[color_class]
        p['style'] = path_style + color

# now go through all of the groups and update the style
for g in gs:
        try:
            rate = penetration[g['id']]
        except:
            continue

        if rate > 90:
            color_class = 5
        elif rate > 75:
            color_class = 4
        elif rate > 60:
            color_class = 3
        elif rate > 45:
            color_class = 2
        elif rate > 30:
            color_class = 1
        else:
            color_class = 0

        # set the color we are going to use and then update the style
        color = colors[color_class]
        g['style'] = path_style + color
        # loop through all the paths within this group and update all of their styles too
        for t in g.findAll('path',recursive=True):
            t['style'] = path_style + color


# write everything out to file
f = open("newfile.svg", "w")
# it's really important that "viewBox" is correctly capitalized and BeautifulSoup kills the capitalization in my tests
f.write(str(soup).replace('viewbox','viewBox',1))

