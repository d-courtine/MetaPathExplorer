#! /usr/bin/python2
# version 0.1.0
#########################################################################################
# MetaPathExplorer_pathway allows to dowload color pathway map 							#
#########################################################################################

#########################################################################################
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, ##
## INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A       ##
## PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT  ##
## HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION   ##
## OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE      ##
## SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                              ##        #########################################################################################

'''
    MetaPathExplorer_pathway take as entries a list of KEGG Orthologous groups (KOs), a KEGG pathway 
    map id and a color to downloading the colouring pathway from Search&Color Pathway mapping tool 
    from KEGG (http://www.genome.jp/kegg/tool/map_pathway2.html) 
    
    Script run under Python 2.7
''' 

# librairies 
from __future__ import division
from mechanize import Browser
from collections import defaultdict
import os, os.path
import re
import argparse
import sys

####################################################################
# Class 
class KEGG(Browser):
    
    def KEGG_initialisation(self):
        # Initializing 
        self._factory.is_html = True
        self.set_handle_robots(False)
        self.open('https://www.kegg.jp/kegg/mapper/color.html')
        self.KEGG_STATE = 'initialized'

    def search_pathways(self, K0s, color, org):
        # 'searching for pathways'
        if self.KEGG_STATE != 'initialized':
            self.KEGG_initialisation()

        K0_data = ''

        # associate present K0 with the choosen color
        for K0 in K0s:
            K0_data += '%s %s\n' % (K0, color)
        
        self.select_form(nr = 0)
        self['unclassified'] = K0_data	# K0 list
        self['org'] = org 				# organism option
        self.submit()
        self.KEGG_STATE = 'submited'

    def get_pathway_from_url(self, url):
        
        return url.split('/')[-1].split('.')[0]

    def download_pathway_from_link(self, link, imgpath):
        
        assert self.KEGG_STATE == 'submited'
        resp = self.follow_link(link = link)
        # 'downloading' colouring pathway map
        try:
            follow = resp.get_data()
            img_path = re.findall('<img src="([\d\w/.]*?)"', follow)[0]
            self.retrieve('https://www.kegg.jp/' + img_path, imgpath)
        finally:
            self.back()
        
    def get_pathway_from_submission(self, pathway, imgpath, pathway_dl = None):

        assert self.KEGG_STATE == 'submited'
        #  recover only the link of the pathway of interest 
        link = [ln for ln in self.links() if (ln.url.startswith('/kegg-bin') and self.get_pathway_from_url(ln.url) == pathway)]
        if len(link) == 1 :
            self.download_pathway_from_link(link[0], imgpath)
        else :
            print os.path.realpath(__file__)+' (error): ' + pathway + ' do not contain the given KO list.'

#####################################################################
# Function
def get_kegg_image(tdir, K0s, color, pathway, org):
    
    kegg = KEGG()
    kegg.KEGG_initialisation()
    kegg.search_pathways(K0s, color = color, org = org)
    kegg.get_pathway_from_submission(pathway = pathway, imgpath = tdir)

#####################################################################
# Main
if __name__ == '__main__':
    
    #################################################################
    # Recover arguments
    parser = argparse.ArgumentParser(description = 'Recover Pathway Map Image from a list of K0 and pathway name')
    parser.add_argument('--K0file', dest = 'K0file', required = True,
                            help = 'path to file which contains the K0 list.')
    parser.add_argument('--out', dest = 'out', required = True, 
                            help = 'absolute path for the created pathway map.')
    parser.add_argument('--color', dest = 'color', required = True, 
                            help = 'color for KEGG orthologous groups.')
    parser.add_argument('--pathway', dest = 'pathway', required = True, 
                            help = 'pathway name')
    parser.add_argument('--org', dest = 'org', required = False, 
                            help = 'organism name.')

    #################################################################
    # Parse arguments
    args = parser.parse_args()

    #################################################################
    # Reads the K0 list file 
    K0_list = open(args.K0file,'r').read().split('\n')

    #################################################################
    # Launch the KEGG pathway map recovery
    get_kegg_image(args.out, K0_list, args.color, args.pathway, args.org)


#####################################################################
# End of Script