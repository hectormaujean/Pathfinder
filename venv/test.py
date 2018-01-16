import csv    # spreadsheet output
import re     # pattern matching
import sys    # command-line arguments
import zlib   # decompression

# find deflated sections
PARENT = b"FlateDecode"
PARENTLEN = len(PARENT)
START = b"stream\r\n"
STARTLEN = len(START)
END   = b"\r\nendstream"
ENDLEN = len(END)

# find output text in PostScript Tj and TJ fields
PS_TEXT = re.compile(r"(?<!\\)\((.*?)(?<!\\)\)")
print(PS_TEXT)
# return desired per-person records
RECORD = re.compile(r"Name : (.*?)Relation : (.*?)Address : (.*?)Age : (\d+)\s+Sex : (\w?)\s+(\d+)", re.DOTALL)

def get_streams(byte_data):
    streams = []
    start_at = 0
    while True:
        # find block containing compressed data
        p = byte_data.find(PARENT, start_at)
        if p == -1:
            # no more streams
            break
        # find start of data
        s = byte_data.find(START, p + PARENTLEN)
        if s == -1:
            raise ValueError("Found parent at {} bytes with no start".format(p))
        # find end of data
        e = byte_data.find(END, s + STARTLEN)
        if e == -1:
            raise ValueError("Found start at {} bytes but no end".format(s))
        # unpack compressed data
        block = byte_data[s + STARTLEN:e]
        unc = zlib.decompress(block)
        streams.append(unc)
        start_at = e + ENDLEN
    return streams

def depostscript(text):
    out = []
    for line in text.splitlines():
        if line.endswith(" Tj"):
            # new output line
            s = "".join(PS_TEXT.findall(line))
            out.append(s)
        elif line.endswith(" TJ"):
            # continued output line
            s = "".join(PS_TEXT.findall(line))
            out[-1] += s
    return "\n".join(out)

def main(in_pdf, out_csv):
    # load .pdf file into memory
    with open(in_pdf, "rb") as f:
        pdf = f.read()

    # get content of all compressed streams
    # NB: sample file results in 32 streams
    streams = get_streams(pdf)

    # we only want the streams which contain text data
    # NB: sample file results in 22 text streams
    text_streams = []
    for stream in streams:
        try:
            text = stream.decode()
            text_streams.append(text)
        except UnicodeDecodeError:
            pass

    # of the remaining blocks, we only want those containing the text '(Relation : '
    # NB: sample file results in 4 streams
    text_streams = [t for t in text_streams if '(Relation : ' in t]

    # consolidate target text
    # NB: sample file results in 886 lines of text
    text = "\n".join(depostscript(ts) for ts in text_streams)

    # pull desired data from text
    records = []
    for name,relation,address,age,sex,num in RECORD.findall(text):
        name = name.strip()
        relation = relation.strip()
        t = address.strip().splitlines()
        code = t[-1]
        address = " ".join(t[:-1])
        age = int(age)
        sex = sex.strip()
        num = int(num)
        records.append((num, code, name, relation, address, age, sex))

    # save results as csv
    with open(out_csv, "w", newline='') as outf:
        wr = csv.writer(outf)
        wr.writerows(records)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python {} input.pdf output.csv".format(__name__))
    else:
        main(sys.argv[1], sys.argv[2])