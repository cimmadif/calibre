#define UNICODE
#define PY_SSIZE_T_CLEAN
#ifndef _FILE_OFFSET_BITS
#define _FILE_OFFSET_BITS 64
#endif

#include <Python.h>
#include <datetime.h>
#include <errno.h>

#include <stdlib.h>
#include <fcntl.h>
#include <stdio.h>
#define _USE_MATH_DEFINES
#include <math.h>
#include <string.h>

#define MIN(x, y) ((x < y) ? x : y)
#define MAX(x, y) ((x > y) ? x : y)
#define CLAMP(value, lower, upper) ((value > upper) ? upper : ((value < lower) ? lower : value))
#define STRIDE(width, r, c) ((width * (r)) + (c))

#ifdef _MSC_VER
#ifndef uint32_t
typedef unsigned __int32 uint32_t;
#endif

#ifndef uint8_t
typedef unsigned __int8 uint8_t;
#endif
#else
#include <stdint.h>
#endif
#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

static PyObject*
barename(PyObject *self, PyObject *tag) {
    if (!PyUnicode_Check(tag)) { PyErr_Format(PyExc_TypeError, "%R is not a unicode string", tag); return NULL; }
    Py_ssize_t pos = PyUnicode_FindChar(tag, '}', 0, PyUnicode_GetLength(tag), -1);
    switch(pos) {
        case -2: return NULL;
        case -1: Py_INCREF(tag); return tag;
        default: return PyUnicode_Substring(tag, pos + 1, PyUnicode_GetLength(tag));
    }
}

static PyObject*
namespace(PyObject *self, PyObject *tag) {
    if (!PyUnicode_Check(tag)) { PyErr_Format(PyExc_TypeError, "%R is not a unicode string", tag); return NULL; }
    Py_ssize_t pos = PyUnicode_FindChar(tag, '}', 0, PyUnicode_GetLength(tag), -1);
    switch(pos) {
        case -2: return NULL;
        case -1: return PyUnicode_FromString("");
        default: return PyUnicode_Substring(tag, 1, pos);
    }
}


static PyObject *
speedup_parse_date(PyObject *self, PyObject *args) {
    const char *raw, *orig, *tz;
    char *end;
    long year, month, day, hour, minute, second, tzh = 0, tzm = 0, sign = 0;
    size_t len;
    if(!PyArg_ParseTuple(args, "s", &raw)) return NULL;
    while ((*raw == ' ' || *raw == '\t' || *raw == '\n' || *raw == '\r' || *raw == '\f' || *raw == '\v') && *raw != 0) raw++;
    len = strlen(raw);
    if (len < 19) Py_RETURN_NONE;

    orig = raw;

    year = strtol(raw, &end, 10);
    if ((end - raw) != 4) Py_RETURN_NONE;
    raw += 5;


    month = strtol(raw, &end, 10);
    if ((end - raw) != 2) Py_RETURN_NONE;
    raw += 3;

    day = strtol(raw, &end, 10);
    if ((end - raw) != 2) Py_RETURN_NONE;
    raw += 3;

    hour = strtol(raw, &end, 10);
    if ((end - raw) != 2) Py_RETURN_NONE;
    raw += 3;

    minute = strtol(raw, &end, 10);
    if ((end - raw) != 2) Py_RETURN_NONE;
    raw += 3;

    second = strtol(raw, &end, 10);
    if ((end - raw) != 2) Py_RETURN_NONE;

    tz = orig + len - 6;

    if (*tz == '+') sign = +1;
    if (*tz == '-') sign = -1;
    if (sign != 0) {
        // We have TZ info
        tz += 1;

        tzh = strtol(tz, &end, 10);
        if ((end - tz) != 2) Py_RETURN_NONE;
        tz += 3;

        tzm = strtol(tz, &end, 10);
        if ((end - tz) != 2) Py_RETURN_NONE;
    }

    return Py_BuildValue("lllllll", year, month, day, hour, minute, second,
            (tzh*60 + tzm)*sign*60);
}


static PyObject*
speedup_pdf_float(PyObject *self, PyObject *args) {
    double f = 0.0, a = 0.0;
    char *buf = "0", *dot;
    void *free_buf = NULL;
    int precision = 6, l = 0;
    PyObject *ret;

    if(!PyArg_ParseTuple(args, "d", &f)) return NULL;

    a = fabs(f);

    if (a > 1.0e-7) {
        if(a > 1) precision = MIN(MAX(0, 6-(int)log10(a)), 6);
        buf = PyOS_double_to_string(f, 'f', precision, 0, NULL);
        if (buf != NULL) {
            free_buf = (void*)buf;
            if (precision > 0) {
                l = (int)(strlen(buf) - 1);
                while (l > 0 && buf[l] == '0') l--;
                if (buf[l] == ',' || buf[l] == '.') buf[l] = 0;
                else buf[l+1] = 0;
                if ( (dot = strchr(buf, ',')) ) *dot = '.';
            }
        } else if (!PyErr_Occurred()) PyErr_SetString(PyExc_TypeError, "Float->str failed.");
    }

    ret = PyUnicode_FromString(buf);
    if (free_buf != NULL) PyMem_Free(free_buf);
    return ret;
}

static PyObject*
speedup_detach(PyObject *self, PyObject *args) {
    char *devnull = NULL;
    if (!PyArg_ParseTuple(args, "s", &devnull)) return NULL;
    if (freopen(devnull, "r", stdin) == NULL) return PyErr_SetFromErrnoWithFilename(PyExc_OSError, devnull);
    if (freopen(devnull, "w", stdout) == NULL) return PyErr_SetFromErrnoWithFilename(PyExc_OSError, devnull);
    if (freopen(devnull, "w", stderr) == NULL)  return PyErr_SetFromErrnoWithFilename(PyExc_OSError, devnull);
    Py_RETURN_NONE;
}

static void calculate_gaussian_kernel(Py_ssize_t size, double *kernel, double radius) {
    const double sqr = radius * radius;
    const double factor = 1.0 / (2 * M_PI * sqr);
    const double denom = 2 * sqr;
    double *t, sum = 0;
    Py_ssize_t r, c, center = size / 2;

    for (r = 0; r < size; r++) {
        t = kernel + (r * size);
        for (c = 0; c < size; c++) {
            t[c] = factor * pow(M_E, - ( ( (r - center) * (r - center) + (c - center) * (c - center) ) / denom ));
        }
    }

    // Normalize matrix
    for (r = 0; r < size * size; r++) sum += kernel[r];
    sum = 1 / sum;
    for (r = 0; r < size * size; r++) kernel[r] *= sum;
}

static PyObject*
speedup_create_texture(PyObject *self, PyObject *args, PyObject *kw) {
    PyObject *ret = NULL;
    Py_ssize_t width, height, weight = 3, i, j, r, c, half_weight;
    double pixel, *mask = NULL, radius = 1, *kernel = NULL, blend_alpha = 0.1;
    float density = 0.7f;
    unsigned char base_r, base_g, base_b, blend_r = 0, blend_g = 0, blend_b = 0, *ppm = NULL, *t = NULL;
    char header[100] = {0};
    static char* kwlist[] = {"blend_red", "blend_green", "blend_blue", "blend_alpha", "density", "weight", "radius", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kw, "nnbbb|bbbdfnd", kwlist, &width, &height, &base_r, &base_g, &base_b, &blend_r, &blend_g, &blend_b, &blend_alpha, &density, &weight, &radius)) return NULL;
    if (weight % 2 != 1 || weight < 1) { PyErr_SetString(PyExc_ValueError, "The weight must be an odd positive number"); return NULL; }
    if (radius <= 0) { PyErr_SetString(PyExc_ValueError, "The radius must be positive"); return NULL; }
    if (width > 100000 || height > 10000) { PyErr_SetString(PyExc_ValueError, "The width or height is too large"); return NULL; }
    if (width < 1 || height < 1) { PyErr_SetString(PyExc_ValueError, "The width or height is too small"); return NULL; }
    snprintf(header, sizeof(header)-1, "P6\n%d %d\n255\n", (int)width, (int)height); // NOLINT

    kernel = (double*)calloc(weight * weight, sizeof(double));
    if (kernel == NULL) { PyErr_NoMemory(); return NULL; }
    mask = (double*)calloc(width * height, sizeof(double));
    if (mask == NULL) { free(kernel); PyErr_NoMemory(); return NULL;}
    ppm = (unsigned char*)calloc(strlen(header) + (3 * width * height), sizeof(unsigned char));
    if (ppm == NULL) { free(kernel); free(mask); PyErr_NoMemory(); return NULL; }

    calculate_gaussian_kernel(weight, kernel, radius);

    // Random noise, noisy pixels are blend_alpha, other pixels are 0
    for (i = 0; i < width * height; i++) {
        if (((float)(rand()) / (float)RAND_MAX) <= density) mask[i] = blend_alpha;
    }

    // Blur the noise using the gaussian kernel
    half_weight = weight / 2;
    for (r = 0; r < height; r++) {
        for (c = 0; c < width; c++) {
            pixel = 0;
            for (i = -half_weight; i <= half_weight; i++) {
                for (j = -half_weight; j <= half_weight; j++) {
                    pixel += (*(mask + STRIDE(width, CLAMP(r + i, 0, height - 1), CLAMP(c + j, 0, width - 1)))) * (*(kernel + STRIDE(weight, half_weight + i, half_weight + j)));
                }
            }
            *(mask + STRIDE(width, r, c)) = CLAMP(pixel, 0, 1);
        }
    }

    // Create the texture in PPM (P6) format
    memcpy(ppm, header, strlen(header));  // NOLINT
    t = ppm + strlen(header);
    for (i = 0, j = 0; j < width * height; i += 3, j += 1) {
#define BLEND(src, dest) ( ((unsigned char)(src * mask[j])) + ((unsigned char)(dest * (1 - mask[j]))) )
        t[i] = BLEND(blend_r, base_r);
        t[i+1] = BLEND(blend_g, base_g);
        t[i+2] = BLEND(blend_b, base_b);
    }

    ret = Py_BuildValue("s", ppm);
    free(mask); mask = NULL;
    free(kernel); kernel = NULL;
    free(ppm); ppm = NULL;
    return ret;
}

static PyObject*
speedup_websocket_mask(PyObject *self, PyObject *args) {
	PyObject *data = NULL, *mask = NULL;
	Py_buffer data_buf = {0}, mask_buf = {0};
	Py_ssize_t offset = 0, i = 0;
	char *dbuf = NULL, *mbuf = NULL;
    int ok = 0;

    if(!PyArg_ParseTuple(args, "OO|n", &data, &mask, &offset)) return NULL;

	if (PyObject_GetBuffer(data, &data_buf, PyBUF_SIMPLE|PyBUF_WRITABLE) != 0) return NULL;
	if (PyObject_GetBuffer(mask, &mask_buf, PyBUF_SIMPLE) != 0) goto done;

	dbuf = (char*)data_buf.buf; mbuf = (char*)mask_buf.buf;
	for(i = 0; i < data_buf.len; i++) dbuf[i] ^= mbuf[(i + offset) & 3];
    ok = 1;

done:
    if(data_buf.obj) PyBuffer_Release(&data_buf);
    if(mask_buf.obj) PyBuffer_Release(&mask_buf);
    if (ok) { Py_RETURN_NONE; }
    return NULL;
}

#define UTF8_ACCEPT 0
#define UTF8_REJECT 1

static const uint8_t utf8d[] = {
  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, // 00..1f
  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, // 20..3f
  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, // 40..5f
  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, // 60..7f
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9, // 80..9f
  7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7, // a0..bf
  8,8,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2, // c0..df
  0xa,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x3,0x4,0x3,0x3, // e0..ef
  0xb,0x6,0x6,0x6,0x5,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8,0x8, // f0..ff
  0x0,0x1,0x2,0x3,0x5,0x8,0x7,0x1,0x1,0x1,0x4,0x6,0x1,0x1,0x1,0x1, // s0..s0
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,1, // s1..s2
  1,2,1,1,1,1,1,2,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1, // s3..s4
  1,2,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,3,1,1,1,1,1,1, // s5..s6
  1,3,1,1,1,1,1,3,1,3,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1, // s7..s8
};

#ifdef _MSC_VER
static void __inline
#else
static void inline
#endif
utf8_decode_(uint32_t* state, uint32_t* codep, uint8_t byte) {
  /* Comes from http://bjoern.hoehrmann.de/utf-8/decoder/dfa/
   * Copyright (c) 2008-2009 Bjoern Hoehrmann <bjoern@hoehrmann.de>
   * Used under license: https://opensource.org/licenses/MIT
   */
  uint32_t type = utf8d[byte];

  *codep = (*state != UTF8_ACCEPT) ?
    (byte & 0x3fu) | (*codep << 6) :
    (0xff >> type) & (byte);

  *state = utf8d[256 + *state*16 + type];
}

static PyObject*
utf8_decode(PyObject *self, PyObject *args) {
	uint8_t *dbuf = NULL;
	uint32_t state = UTF8_ACCEPT, codep = 0, *buf = NULL;
	PyObject *data_obj = NULL, *ans = NULL;
	Py_buffer pbuf;
	Py_ssize_t i = 0, pos = 0;

    if(!PyArg_ParseTuple(args, "O|II", &data_obj, &state, &codep)) return NULL;
	if (PyObject_GetBuffer(data_obj, &pbuf, PyBUF_SIMPLE) != 0) return NULL;
	buf = (uint32_t*)PyMem_Malloc(sizeof(uint32_t) * pbuf.len);
	if (buf == NULL) goto error;
	dbuf = (uint8_t*)pbuf.buf;

	for (i = 0; i < pbuf.len; i++) {
		utf8_decode_(&state, &codep, dbuf[i]);
		if (state == UTF8_ACCEPT) buf[pos++] = codep;
		else if (state == UTF8_REJECT) { PyErr_SetString(PyExc_ValueError, "Invalid byte in UTF-8 string"); goto error; }
	}
	ans = PyUnicode_DecodeUTF32((const char*)buf, pos * sizeof(uint32_t), "strict", NULL);
error:
    if (pbuf.obj) PyBuffer_Release(&pbuf);
	if (buf) { PyMem_Free(buf); buf = NULL; }
	if (ans == NULL) return ans;
	return Py_BuildValue("NII", ans, state, codep);
}

static PyObject*
clean_xml_chars(PyObject *self, PyObject *text) {
    PyObject *result = NULL;
    void *result_text = NULL;
    Py_ssize_t src_i, target_i;
    enum PyUnicode_Kind text_kind;
    Py_UCS4 ch;

    if (!PyUnicode_Check(text)) {
        PyErr_SetString(PyExc_TypeError, "A unicode string is required");
        return NULL;
    }
    if(PyUnicode_READY(text) != 0) {
        // just return null, an exception is already set by READY()
        return NULL;
    }
    if(PyUnicode_GET_LENGTH(text) == 0) {
        // make sure that malloc(0) will never happen
        return text;
    }

    text_kind = PyUnicode_KIND(text);
    // Once we've called READY(), our string is in canonical form, which means
    // it is encoded using UTF-{8,16,32}, such that each codepoint is one
    // element in the array. The value of the Kind enum is the size of each
    // character.
    result_text = malloc(PyUnicode_GET_LENGTH(text) * text_kind);
    if (result_text == NULL) return PyErr_NoMemory();

    target_i = 0;
    for (src_i = 0; src_i < PyUnicode_GET_LENGTH(text); src_i++) {
        ch = PyUnicode_READ(text_kind, PyUnicode_DATA(text), src_i);
        // based on https://en.wikipedia.org/wiki/Valid_characters_in_XML#Non-restricted_characters
        // python 3.3+ unicode strings never contain surrogate pairs, since if
        // they did, they would be represented as UTF-32
        if ((0x20 <= ch && ch <= 0x7e) ||
                ch == 0x9 || ch == 0xa || ch == 0xd || ch == 0x85 ||
				(0x00A0 <= ch && ch <= 0xD7FF) ||
				(0xE000 <= ch && ch <= 0xFDCF) ||
				(0xFDF0 <= ch && ch <= 0xFFFD) ||
                (0xffff < ch && ch <= 0x10ffff)) {
            PyUnicode_WRITE(text_kind, result_text, target_i, ch);
            target_i += 1;
        }
    }

    // using text_kind here is ok because we don't create any characters that
    // are larger than might already exist
    result = PyUnicode_FromKindAndData(text_kind, result_text, target_i);
    free(result_text);
    return result;
}

static PyObject *
speedup_iso_8601(PyObject *self, PyObject *args) {
    char *str = NULL, *c = NULL;
    int year = 0, month = 0, day = 0, hour = 0, minute = 0, second = 0, usecond = 0, i = 0, tzhour = 1000, tzminute = 0, tzsign = 0;

    if (!PyArg_ParseTuple(args, "s", &str)) return NULL;
    c = str;

#define RAISE(msg) return PyErr_Format(PyExc_ValueError, "%s is not a valid ISO 8601 datestring: %s", str, msg);
#define CHAR_IS_DIGIT(c) (*c >= '0' && *c <= '9')
#define READ_DECIMAL_NUMBER(max_digits, x, abort) \
    for (i = 0; i < max_digits; i++) { \
        if (CHAR_IS_DIGIT(c)) x = 10 * x + *c++ - '0'; \
        else { abort; } \
    }
#define OPTIONAL_SEPARATOR(x) if(*c == x) c++;

    // Ignore leading whitespace
    while(*c == ' ' || *c == '\n' || *c == '\r' || *c == '\t' || *c == '\v' || *c == '\f') c++;

    // Year
    READ_DECIMAL_NUMBER(4, year, RAISE("No year specified"));
    OPTIONAL_SEPARATOR('-');
    // Month (optional)
    READ_DECIMAL_NUMBER(2, month, break);
    if (month == 0) month = 1; // YYYY format
    else {
        OPTIONAL_SEPARATOR('-');

        // Day (optional)
        READ_DECIMAL_NUMBER(2, day, break);
    }
    if (day == 0) day = 1; // YYYY-MM format
    if (month > 12) RAISE("month greater than 12");

    if (*c == 'T' || *c == ' ') // Time separator
    {
        c++;

        // Hour
        READ_DECIMAL_NUMBER(2, hour, RAISE("No hour specified"));
        OPTIONAL_SEPARATOR(':');
        // Minute (optional)
        READ_DECIMAL_NUMBER(2, minute, break);
        OPTIONAL_SEPARATOR(':');
        // Second (optional)
        READ_DECIMAL_NUMBER(2, second, break);

        if (*c == '.' || *c == ',') // separator for microseconds
        {
            c++;
            // Parse fraction of second up to 6 places
            READ_DECIMAL_NUMBER(6, usecond, break);
            // Omit excessive digits
            while (CHAR_IS_DIGIT(c)) c++;
            // If we break early, fully expand the usecond
            while (i++ < 6) usecond *= 10;
        }
    }

    switch(*c) {
        case 'Z':
            tzhour = 0; c++; break;
        case '+':
            tzsign = 1; c++; break;
        case '-':
            tzsign = -1; c++; break;
        default:
            break;
    }

    if (tzsign != 0) {
        tzhour = 0;
        READ_DECIMAL_NUMBER(2, tzhour, break);
        OPTIONAL_SEPARATOR(':');
        READ_DECIMAL_NUMBER(2, tzminute, break);
    }

    return Py_BuildValue("NOi", PyDateTime_FromDateAndTime(year, month, day, hour, minute, second, usecond), (tzhour == 1000) ? Py_False : Py_True, tzsign*60*(tzhour*60 + tzminute));
}

#ifndef _MSC_VER
#include <pthread.h>
#if defined(__FreeBSD__) || defined(__OpenBSD__)
#define FREEBSD_SET_NAME
#endif
#if defined(__APPLE__)
// I can't figure out how to get pthread.h to include this definition on macOS. MACOSX_DEPLOYMENT_TARGET does not work.
extern int pthread_setname_np(const char *name);
#elif defined(FREEBSD_SET_NAME)
// Function has a different name on FreeBSD
void pthread_set_name_np(pthread_t tid, const char *name);
#elif defined(__NetBSD__)
// pthread.h provides the symbol
#elif defined(__HAIKU__)
// Haiku doesn't support pthread_set_name_np yet
#else
// Need _GNU_SOURCE for pthread_setname_np on linux and that causes other issues on systems with old glibc
extern int pthread_setname_np(pthread_t, const char *name);
#endif
#endif


static PyObject*
set_thread_name(PyObject *self, PyObject *args) {
	(void)(self); (void)(args);
#if defined(_MSC_VER) || defined(__HAIKU__)
	PyErr_SetString(PyExc_RuntimeError, "Setting thread names not supported on this platform");
	return NULL;
#else
	char *name;
	int ret;
	if (!PyArg_ParseTuple(args, "s", &name)) return NULL;
	while (1) {
		errno = 0;
#if defined(__APPLE__)
		ret = pthread_setname_np(name);
#elif defined(FREEBSD_SET_NAME)
		pthread_set_name_np(pthread_self(), name);
		ret = 0;
#elif defined(__NetBSD__)
		ret = pthread_setname_np(pthread_self(), "%s", name);
#else
		ret = pthread_setname_np(pthread_self(), name);
#endif
		if (ret != 0 && (errno == EINTR || errno == EAGAIN)) continue;
		break;
	}
    if (ret != 0) { PyErr_SetFromErrno(PyExc_OSError); return NULL; }
	Py_RETURN_NONE;
#endif
}

#define char_is_ignored(ch) (ch <= 32)

typedef struct udata {
    void *data; int kind; Py_ssize_t len;
} udata;

static size_t
count_chars_in(udata *text) {
	size_t ans = text->len;
	for (Py_ssize_t i = 0; i < text->len; i++) if (char_is_ignored(PyUnicode_READ(text->kind, text->data, i))) ans--;
	return ans;
}

static size_t
count_chars(const char *tag_name, Py_ssize_t tag_len, udata *text, udata *tail) {
	size_t ans = 0;
    int is_ignored_tag = 0;
    char ltagname[16];
    if (tag_name) {
        const char *b = memchr(tag_name, '}', tag_len);
        if (b) {
            b++;
            tag_len -= b - tag_name;
            tag_name = b;
        }
        if (tag_len < sizeof(ltagname)) {
            memcpy(ltagname, tag_name, tag_len);
            for (size_t i = 0; i < tag_len; i++) if ('A' <= ltagname[i] && ltagname[i] <= 'Z') ltagname[i] += 32;
#define EQ(x) (memcmp(ltagname, #x, tag_len) == 0)
            switch(ltagname[0]) {
                case 's':
                    if (EQ(script) || EQ(style)) is_ignored_tag = 1;
                    else if (EQ(svg)) ans += 1000;
                    break;
                case 'n':
                    if (EQ(noscript)) is_ignored_tag = 1;
                    break;
                case 't':
                    if (EQ(title)) is_ignored_tag = 1;
                    break;
                case 'i':
                    if (EQ(img)) ans += 1000;
                    break;
            }
        }
    }
#undef EQ
	ans += count_chars_in(tail);
	if (!is_ignored_tag) ans += count_chars_in(text);
    return ans;
}

static PyObject*
get_num_of_significant_chars(PyObject *self, PyObject *elem) {
	(void)(self);
	const char *tag_name = NULL;
    Py_ssize_t tag_len = 0;
    PyObject *ptn = PyObject_GetAttrString(elem, "tag"), *text = NULL;
    if (ptn && PyUnicode_Check(ptn)) tag_name = PyUnicode_AsUTF8AndSize(ptn, &tag_len);
    udata xdata = {0}, tdata = {0};
    if (tag_name) {
        text = PyObject_GetAttrString(elem, "text");
        if (text && PyUnicode_Check(text)) {
            xdata.len = PyUnicode_GET_LENGTH(text); xdata.kind = PyUnicode_KIND(text); xdata.data = PyUnicode_DATA(text);
        }
    }
    PyObject *tail = PyObject_GetAttrString(elem, "tail");
    if (tail && PyUnicode_Check(tail)) {
        tdata.len = PyUnicode_GET_LENGTH(tail); tdata.kind = PyUnicode_KIND(tail); tdata.data = PyUnicode_DATA(tail);
    }
    size_t ans;
    Py_BEGIN_ALLOW_THREADS
        ans = count_chars(tag_name, tag_len, &xdata, &tdata);
    Py_END_ALLOW_THREADS;
    Py_XDECREF(ptn); Py_XDECREF(text); Py_XDECREF(tail);
	return PyLong_FromSize_t(ans);
}


typedef struct deepcopy_data {
    PyObject *python_deepcopy, *memo;
} deepcopy_data;

static PyObject* deepcopy_object(PyObject *, deepcopy_data *);

static PyObject*
insert_into_cache(PyObject *o, deepcopy_data *d) {
    if (!o) return NULL;
    PyObject *key = PyLong_FromVoidPtr(o);
    if (!key) { Py_DECREF(o); return NULL; }
    if (PyDict_SetItem(d->memo, key, o) != 0) { Py_DECREF(key); Py_DECREF(o); return NULL; }
    return o;
}

static PyObject*
deepcopy_list(PyObject *o, deepcopy_data *d) {
    PyObject *ans = insert_into_cache(PyList_New(PyList_GET_SIZE(o)), d);
    if (!ans) return NULL;
    for (Py_ssize_t i = 0; i < PyList_GET_SIZE(o); i++) {
        PyObject *t = deepcopy_object(PyList_GET_ITEM(o, i), d);
        if (!t) { Py_CLEAR(t); return NULL; }
        PyList_SET_ITEM(ans, i, t);
    }
    return ans;
}

static PyObject*
deepcopy_tuple(PyObject *o, deepcopy_data *d) {
    PyObject *ans = insert_into_cache(PyTuple_New(PyTuple_GET_SIZE(o)), d);
    if (!ans) return NULL;
    for (Py_ssize_t i = 0; i < PyTuple_GET_SIZE(o); i++) {
        PyObject *t = deepcopy_object(PyTuple_GET_ITEM(o, i), d);
        if (!t) { Py_CLEAR(ans); return NULL; }
        PyTuple_SET_ITEM(ans, i, t);
    }
    return ans;
}


static PyObject*
deepcopy_dict(PyObject *o, deepcopy_data *d) {
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    PyObject *ans = insert_into_cache(PyDict_New(), d);
    if (!ans) return NULL;

    while (PyDict_Next(o, &pos, &key, &value)) {
        PyObject *tk = deepcopy_object(key, d);
        if (!tk) break;
        PyObject *tv = deepcopy_object(value, d);
        if (!tv) { Py_DECREF(tk); break; }
        int ok = PyDict_SetItem(ans, tk, tv) == 0;
        Py_DECREF(tk); Py_DECREF(tv);
        if (!ok) break;
    }
    if (PyErr_Occurred()) { Py_DECREF(ans); return NULL; }
    return ans;
}

static PyObject*
deepcopy_set(PyObject *o, deepcopy_data *d, int is_frozen) {
    PyObject *ans = insert_into_cache(is_frozen ? PyFrozenSet_New(NULL) : PySet_New(NULL), d);
    if (!ans) return NULL;
    PyObject *iter = PyObject_GetIter(o);
    if (!iter) { Py_DECREF(ans); return NULL; }
    PyObject *key;
    while ((key = PyIter_Next(iter)) != NULL) {
        PyObject *t = deepcopy_object(key, d);
        if (!t) break;
        if (PySet_Add(ans, t) != 0) { Py_DECREF(t); break; }
    }
    Py_DECREF(iter);
    if (PyErr_Occurred()) { Py_DECREF(ans); return NULL; }
    return ans;
}

static PyObject*
deepcopy_object(PyObject *o, deepcopy_data *d) {
    PyObject *key = PyLong_FromVoidPtr(o);
    if (!key) return NULL;
    PyObject *cached = PyDict_GetItem(d->memo, key);
    Py_DECREF(key);
    if (cached) return Py_NewRef(cached);
    PyTypeObject *type;
    // Fast case for builtin immutable types
    if (
        o == Py_None || o == Py_True || o == Py_False || (type = Py_TYPE(o)) == &PyUnicode_Type ||
        type == &PyBytes_Type || type == &PyLong_Type || type == &PyFloat_Type || type == &PyMemoryView_Type ||
        type == &PyComplex_Type || type == &PyType_Type || type == &PyFunction_Type || type == &PyCode_Type ||
        o == Py_Ellipsis || o == Py_NotImplemented
    ) return Py_NewRef(o);
    if (type == &PyList_Type) return deepcopy_list(o, d);
    if (type == &PyTuple_Type) return deepcopy_tuple(o, d);
    if (type == &PyDict_Type) return deepcopy_dict(o, d);
    if (type == &PySet_Type) return deepcopy_set(o, d, 0);
    if (type == &PyFrozenSet_Type) return deepcopy_set(o, d, 1);
    if (PyWeakref_Check(o)) return Py_NewRef(o);
    return PyObject_CallFunctionObjArgs(d->python_deepcopy, o, d->memo);
}

static PyObject*
deepcopy(PyObject *self, PyObject *o) {
    PyObject *memo = PyDict_New();
    if (!memo) return NULL;
    PyObject *copy_module = PyImport_ImportModule("copy");
    if (!copy_module) { Py_DECREF(memo); return NULL; }
    PyObject *python_deepcopy = PyObject_GetAttrString(copy_module, "deepcopy");
    Py_DECREF(copy_module);
    if (!python_deepcopy) { Py_DECREF(memo); return NULL; }
    deepcopy_data d = {.python_deepcopy = python_deepcopy, .memo = memo};
    PyObject *ans = deepcopy_object(o, &d);
    Py_DECREF(python_deepcopy); Py_DECREF(memo);
    return ans;
}


static PyObject*
pread_all(PyObject *self, PyObject *args) {
    int fd; unsigned long long n, offset = 0;
    if (!PyArg_ParseTuple(args, "iK|K", &fd, &n, &offset)) return NULL;
#ifdef _WIN32
    PyObject *msvcrt = PyImport_ImportModule("msvcrt");
    if (!msvcrt) return NULL;
    PyObject *get_osfhandle = PyObject_GetAttrString(msvcrt, "get_osfhandle");
    Py_CLEAR(msvcrt);
    if (!get_osfhandle) return NULL;
    PyObject *ret = PyObject_CallFunctionObjArgs(get_osfhandle, PyTuple_GET_ITEM(args, 0), NULL);
    Py_CLEAR(get_osfhandle);
    if (!ret) return NULL;
    HANDLE file = (HANDLE)PyLong_AsUnsignedLongLong(ret);
    Py_CLEAR(ret);
#endif
    PyObject *output = PyBytes_FromStringAndSize(NULL, n);
    if (!output || !n) return output;
    size_t pos = 0;
    char *buf = PyBytes_AS_STRING(output);
    int saved_errno = 0;
    Py_BEGIN_ALLOW_THREADS;
    while (pos < n) {
#ifdef _WIN32
        DWORD nr = 0;
        OVERLAPPED overlapped;
        memset(&overlapped, 0, sizeof(OVERLAPPED));
        overlapped.OffsetHigh = (uint32_t)((offset & 0xFFFFFFFF00000000LL) >> 32);
        overlapped.Offset = (uint32_t)(offset & 0xFFFFFFFFLL);
        SetLastError(0);
        BOOL ok = ReadFile(file, buf + pos, n - pos, &nr, &overlapped);
        if (!ok) {
            DWORD err = GetLastError();
            if (err != ERROR_HANDLE_EOF) saved_errno = err;
            break;
        }
#else
        ssize_t nr = pread(fd, buf + pos, n - pos, offset);
        if (nr < 0) {
            if (errno == EINTR || errno == EAGAIN) continue;
            saved_errno = errno;
            break;
        } else if (nr == 0) break;
#endif
        pos += nr;
        offset += nr;
    }
    Py_END_ALLOW_THREADS
    if (saved_errno != 0) {
        Py_CLEAR(output);
#ifdef _WIN32
        PyErr_SetFromWindowsErr(saved_errno);
#else
        errno = saved_errno;
        PyErr_SetFromErrno(PyExc_OSError);
#endif
        return NULL;
    }
    if (pos < n && _PyBytes_Resize(&output, pos) != 0) return NULL;
    return output;
}

static PyMethodDef speedup_methods[] = {
    {"deepcopy", deepcopy, METH_O,
        "deepcopy(object)\n\nFast implementation of deepcopy()"
    },

    {"parse_date", speedup_parse_date, METH_VARARGS,
        "parse_date()\n\nParse ISO dates faster (specialized for dates stored in the calibre db)."
    },

    {"parse_iso8601", speedup_iso_8601, METH_VARARGS,
        "parse_iso8601(datestring)\n\nParse ISO 8601 dates faster. More spec compliant than parse_date()"
    },

    {"pdf_float", speedup_pdf_float, METH_VARARGS,
        "pdf_float()\n\nConvert float to a string representation suitable for PDF"
    },

    {"detach", speedup_detach, METH_VARARGS,
        "detach()\n\nRedirect the standard I/O stream to the specified file (usually os.devnull)"
    },

    {"create_texture", (PyCFunction)speedup_create_texture, METH_VARARGS | METH_KEYWORDS,
        "create_texture(width, height, red, green, blue, blend_red=0, blend_green=0, blend_blue=0, blend_alpha=0.1, density=0.7, weight=3, radius=1)\n\n"
            "Create a texture of the specified width and height from the specified color."
            " The texture is created by blending in random noise of the specified blend color into a flat image."
            " All colors are numbers between 0 and 255. 0 <= blend_alpha <= 1 with 0 being fully transparent."
            " 0 <= density <= 1 is used to control the amount of noise in the texture."
            " weight and radius control the Gaussian convolution used for blurring of the noise. weight must be an odd positive integer. Increasing the weight will tend to blur out the noise. Decreasing it will make it sharper."
            " This function returns an image (bytestring) in the PPM format as the texture."
    },

    {"websocket_mask", speedup_websocket_mask, METH_VARARGS,
        "websocket_mask(data, mask [, offset=0)\n\nXOR the data (bytestring) with the specified (must be 4-byte bytestring) mask"
    },

	{"utf8_decode", utf8_decode, METH_VARARGS,
		"utf8_decode(data, [, state=0, codep=0)\n\nDecode an UTF-8 bytestring, using a strict UTF-8 decoder, that unlike python does not allow orphaned surrogates. Returns a unicode object and the state."
	},

    {"clean_xml_chars", clean_xml_chars, METH_O,
        "clean_xml_chars(unicode_object)\n\nRemove codepoints in unicode_object that are not allowed in XML"
    },

	{"set_thread_name", set_thread_name, METH_VARARGS,
		"set_thread_name(name)\n\nWrapper for pthread_setname_np"
	},

	{"pread_all", pread_all, METH_VARARGS,
		"pread_all(fd, n, offset)\n\nRead upto n bytes from the specified fd at offset in a thread safe manner."
        " If less than n bytes are returned it means there were less than n bytes in the file at offset."
        " Only works with seekable regular files, not sockets/ttys/etc. Note that on Windows it moves the file pointer"
        " so cannot be mixed with calls to tell() or ordinary reads."
	},

	{"get_num_of_significant_chars", get_num_of_significant_chars, METH_O,
		"get_num_of_significant_chars(elem)\n\nGet the number of chars in specified tag"
	},

	{"barename", barename, METH_O,
		"barename(tag)\n\nGet bare tag name without namespace"
	},

	{"namespace", namespace, METH_O,
		"namespace(tag)\n\nGet namespace of the tag"
	},

    {NULL, NULL, 0, NULL}
};

static int
exec_module(PyObject *module) {
    PyDateTime_IMPORT;
#ifndef _WIN32
    PyModule_AddIntConstant(module, "O_CLOEXEC", O_CLOEXEC);
#endif
    return 0;
}

static PyModuleDef_Slot slots[] = { {Py_mod_exec, exec_module}, {0, NULL} };

static struct PyModuleDef module_def = {
    .m_base     = PyModuleDef_HEAD_INIT,
    .m_name     = "speedup",
    .m_doc      = "Implementation of methods in C for speed.",
    .m_methods  = speedup_methods,
    .m_slots    = slots,
};

CALIBRE_MODINIT_FUNC PyInit_speedup(void) { return PyModuleDef_Init(&module_def); }
