# =============================================================================
# OWSLib. Copyright (C) 2012 Jachym Cepicky
#
# Contact email: jachym.cepicky@gmail.com
#
# =============================================================================

from __future__ import (absolute_import, division, print_function)

from owscapable.crs import Crs

from urllib.parse import urlencode
import logging
from owscapable.util import log

class WebFeatureService_(object):
    """Base class for WebFeatureService implementations"""

    def getBBOXKVP (self,bbox,typename):
        """Formate bounding box for KVP request type (HTTP GET)

        @param bbox: (minx,miny,maxx,maxy[,srs])
        @type bbox: List
        @param typename:  feature name 
        @type typename: String
        @returns: String properly formated according to version and
            coordinate reference system
        """
        srs = None

        # srs of the bbox is specified in the bbox as fifth paramter
        if len(bbox) == 5:
            srs = self.getSRS(bbox[4],typename[0])
        # take default srs
        else:
            srs = self.contents[typename[0]].crsOptions[0]

        # 1.1.0 and 2.0.0 have same encoding
        if self.version in ["1.1.0","2.0.0"]:

            # format bbox parameter
            if srs.encoding == "urn" :
                    if srs.axisorder == "yx":
                        return "%s,%s,%s,%s,%s" % \
                            (bbox[1],bbox[0],bbox[3],bbox[2],srs.getcodeurn())
                    else:
                        return "%s,%s,%s,%s,%s" % \
                        (bbox[0],bbox[1],bbox[2],bbox[3],srs.getcodeurn())
            else:
                return "%s,%s,%s,%s,%s" % \
                        (bbox[0],bbox[1],bbox[2],bbox[3],srs.getcode())
        # 1.0.0
        else:
            return "%s,%s,%s,%s,%s" % \
                    (bbox[0],bbox[1],bbox[2],bbox[3],srs.getcode())

    def getSRS(self, srsname, typename):
        """Returns None or Crs object for given name

        @param typename:  feature name 
        @type typename: String
        """
        if not isinstance(srsname, Crs):
            srs = Crs(srsname)
        else:
            srs = srsname

        try:
            index = self.contents[typename].crsOptions.index(srs)
            # Return the Crs string that was pulled directly from the
            # GetCaps document (the 'id' attribute in the Crs object).
            return self.contents[typename].crsOptions[index]
        except ValueError:
            options = ", ".join([x.id for x in self.contents[typename].crsOptions])
            log.warning("Requested srsName '%s' not available for requested typename '%s'. \
                         Options are: %s. " % (srs.getcode(), typename, options))
            return None

    def getGETGetFeatureRequest(self, typename=None, filter=None, bbox=None, featureid=None,
                   featureversion=None, propertyname=None, maxfeatures=None,storedQueryID=None, storedQueryParams={},
                   outputFormat=None, method='Get', startindex=None):
        """Formulate proper GetFeature request using KVP encoding
        ----------
        typename : list
            List of typenames (string)
        filter : string 
            XML-encoded OGC filter expression.
        bbox : tuple
            (left, bottom, right, top) in the feature type's coordinates == (minx, miny, maxx, maxy)
        featureid : list
            List of unique feature ids (string)
        featureversion : string
            Default is most recent feature version.
        propertyname : list
            List of feature property names. '*' matches all.
        maxfeatures : int
            Maximum number of features to be returned.
        method : string
            Qualified name of the HTTP DCP method to use.
        outputFormat: string (optional)
            Requested response format of the request.
        startindex: int (optional)
            Start position to return feature set (paging in combination with maxfeatures)

        There are 3 different modes of use

        1) typename and bbox (simple spatial query)
        2) typename and filter (==query) (more expressive)
        3) featureid (direct access to known features)
        """

        base_url = next((m.get('url') for m in self.getOperationByName('GetFeature').methods if m.get('type').lower() == method.lower()))
        base_url = base_url if base_url.endswith("?") else base_url+"?"
            
        request = {'service': 'WFS', 'version': self.version, 'request': 'GetFeature'}
        
        # check featureid
        if featureid:
            request['featureid'] = ','.join(featureid)
        elif bbox:
            request['bbox'] = self.getBBOXKVP(bbox,typename)
        elif filter:
            request['query'] = str(filter)
        if typename:
            typename = [typename] if type(typename) == type("") else typename
            request['typename'] = ','.join(typename)
        if propertyname: 
            request['propertyname'] = ','.join(propertyname)
        if featureversion: 
            request['featureversion'] = str(featureversion)
        if maxfeatures: 
            request['maxfeatures'] = str(maxfeatures)
        if startindex:
            request['startindex'] = str(startindex)
        if storedQueryID: 
            request['storedQuery_id']=str(storedQueryID)
            for param in storedQueryParams:
                request[param]=storedQueryParams[param]
        if outputFormat is not None:
            request["outputFormat"] = outputFormat

        data = urlencode(request)

        return base_url+data
