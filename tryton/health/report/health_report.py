# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
# SPDX-FileCopyrightText: 2023-2025 Feng Shu (tumashu)
#
# SPDX-License-Identifier: GPL-3.0-or-later

#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                           HEALTH package                              #
#   health_report.py: Disease, Medication and Vaccination reports       #
#########################################################################
from datetime import datetime
from trytond.i18n import gettext

import io

from trytond.modules.health.core import get_institution_timezone

try:
    from PIL import Image
except ImportError:
    Image = None


__all__ = ['ReportDateAndTimeMixin',
           'ReportGettextMixin',
           'ReportImageToolMixin']


class ReportDateAndTimeMixin():

    @classmethod
    def get_context(cls, records, header, data):
        context = super(
            ReportDateAndTimeMixin, cls).get_context(
                records, header, data)

        context['print_datetime'] = datetime.now()
        context['tz'] = get_institution_timezone()

        return context


class ReportGettextMixin:
    '''Mixin gettext function and some strings need translation and
    used frequently.

    '''
    __slots__ = ()

    @classmethod
    def get_context(cls, records, header, data):
        context = super(ReportGettextMixin, cls).get_context(
            records, header, data)

        context['yes_str'] = gettext('health.msg_yes_str')
        context['no_str'] = gettext('health.msg_no_str')
        context['gettext'] = gettext

        return context


class ReportImageToolMixin:
    'Mixin to operate image in report.'
    __slots__ = ()

    @classmethod
    def image_keep_size(cls, image):
        """Return a tuple like: (image, mimetype, width, height), which is
        used in relatorio open document's image template, this tuple let
        image keep its pt size.
        """
        try:
            img = Image.open(io.BytesIO(image))
            width, height = img.size

            w = str(width) + 'pt'
            h = str(height) + 'pt'
            mimetype = None

        except BaseException:

            w = None
            h = None
            mimetype = None

        return (image, mimetype, w, h)

    @classmethod
    def image_resize(cls, image, max_width, max_height, unit='cm'):
        """Return a tuple like: (image, mimetype, width, height), which is
        used in relatorio open document's image template, this tuple let
        image showed in odt file keep ratio, and width < max_width, height
        < max_height.
        """
        try:
            img = Image.open(io.BytesIO(image))
            orig_width, orig_height = img.size
            orig_ratio = float(orig_height / orig_width)
            ratio = max_height / max_width

            if orig_ratio >= ratio:
                width = max_height / orig_ratio
                height = max_height
            else:
                width = max_width
                height = max_width * orig_ratio

            w = str(width) + unit
            h = str(height) + unit
            mimetype = None

        except BaseException:

            w = str(max_width) + unit
            h = str(max_height) + unit
            mimetype = None

        return (image, mimetype, w, h)

    @classmethod
    def image_crop(cls, image, width, height, unit='cm'):
        """Center-crop image and return a tuple like:

            (new_image, mimetype, width, height)

        which is used in relatorio open document's image template, this
        tuple let image showed in odt file keep ratio and size = (width,
        height).

        """
        try:
            ratio = height / width
            image_info = cls._image_crop_to_ratio(image, ratio)
            image = image_info.get('image')
            mimetype = image_info.get('mimetype')
        except BaseException:
            image = image
            mimetype = None

        w = str(width) + unit
        h = str(height) + unit
        return (image, mimetype, w, h)

    @classmethod
    def _image_crop_to_ratio(cls, image, ratio):
        """ Center-crop an image, make it conform to the ratio,
        This function is useful to adjust ID card photo.
        """
        img = Image.open(io.BytesIO(image))
        orig_width, orig_height = img.size
        orig_ratio = float(orig_height / orig_width)

        if orig_ratio >= ratio:
            width = orig_width
            height = int(width * ratio)
            x = 0
            y = (orig_height - height) / 2
        else:
            height = orig_height
            width = int(height / ratio)
            x = (orig_width - width) / 2
            y = 0

        regin = (x, y, width + x, height + y)

        new_img = img.crop(regin)

        # Make a PNG image from PIL without the need to create a temp
        # file.
        holder = io.BytesIO()
        new_img.save(holder, format='png')
        new_img_png = holder.getvalue()
        holder.close()

        return {'image': bytearray(new_img_png),
                'mimetype': 'image/png'}

    @classmethod
    def get_context(cls, records, header, data):
        context = super(ReportImageToolMixin, cls).get_context(
            records, header, data)

        context['image_crop'] = cls.image_crop
        context['image_resize'] = cls.image_resize
        context['image_keep_size'] = cls.image_keep_size

        return context
