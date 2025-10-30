#!/usr/bin/env python3
"""
PDF to FB2 Converter
Converts PDF files to FB2 format for e-book readers
"""

import sys
import os
import argparse
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


try:
    import pypdf
except ImportError:
    print("Error: pypdf is not installed")
    print("Install it using: pip install pypdf")
    sys.exit(1)


class PDFToFB2Converter:
    """PDF to FB2 converter"""
    
    def __init__(self, input_file: str, output_file: str = None):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self._generate_output_path()
        
    def _generate_output_path(self) -> Path:
        """Generates output file path"""
        return self.input_file.with_suffix('.fb2')
    
    def _extract_text_from_pdf(self) -> list[str]:
        """Extracts text from PDF file"""
        text_chunks = []
        
        try:
            with open(self.input_file, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                print(f"Total pages: {len(pdf_reader.pages)}")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    print(f"Processing page {page_num}...")
                    text = page.extract_text()
                    if text.strip():
                        text_chunks.append(text)
                
        except Exception as e:
            print(f"Error reading PDF: {e}")
            sys.exit(1)
        
        return text_chunks
    
    def _clean_text(self, text: str) -> str:
        """Cleans text from extra characters"""
        # Remove extra spaces and line breaks
        text = ' '.join(text.split())
        return text
    
    def _create_fb2_document(self, text_chunks: list[str], title: str = None) -> Element:
        """Creates FB2 document"""
        
        # Main FictionBook element
        fictionbook = Element('FictionBook')
        fictionbook.set('xmlns', 'http://www.gribuser.ru/xml/fictionbook/2.0')
        fictionbook.set('xmlns:l', 'http://www.w3.org/1999/xlink')
        
        # Description section
        description = SubElement(fictionbook, 'description')
        
        # Title info
        title_info = SubElement(description, 'title-info')
        
        # Title
        if not title:
            title = self.input_file.stem.replace('_', ' ').title()
        
        book_title = SubElement(title_info, 'book-title')
        book_title.text = title
        
        # Add remaining required elements
        author = SubElement(title_info, 'author')
        first_name = SubElement(author, 'first-name')
        first_name.text = 'Unknown'
        last_name = SubElement(author, 'last-name')
        last_name.text = 'Author'
        
        # Annotation
        annotation = SubElement(title_info, 'annotation')
        p_ann = SubElement(annotation, 'p')
        p_ann.text = f'Converted from {self.input_file.name}'
        
        # Date
        date = SubElement(title_info, 'date')
        date.text = '2024'
        
        # Lang
        lang = SubElement(title_info, 'lang')
        lang.text = 'en'
        
        # Publish info
        publish_info = SubElement(description, 'publish-info')
        
        # Body
        body = SubElement(fictionbook, 'body')
        
        # Title page
        title_page = SubElement(body, 'title')
        title_p = SubElement(title_page, 'p')
        title_p.text = title
        
        # Sections with text
        for chunk in text_chunks:
            section = SubElement(body, 'section')
            
            # Split text into paragraphs
            paragraphs = chunk.split('\n\n')
            
            for para in paragraphs:
                para_clean = self._clean_text(para)
                if para_clean:
                    p = SubElement(section, 'p')
                    p.text = para_clean
        
        return fictionbook
    
    def _save_fb2(self, root: Element):
        """Saves FB2 file"""
        # Make XML pretty
        rough_string = tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent='  ', encoding='utf-8')
        
        # Remove extra XML header
        pretty_xml_str = pretty_xml.decode('utf-8')
        lines = pretty_xml_str.split('\n')
        if lines[0].startswith('<?xml'):
            lines = lines[1:]
        
        # Save file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"\n✓ File saved: {self.output_file}")
    
    def convert(self, title: str = None):
        """Main conversion function"""
        print(f"Converting {self.input_file} to FB2...")
        print(f"Output file: {self.output_file}")
        
        # Extract text
        text_chunks = self._extract_text_from_pdf()
        
        if not text_chunks:
            print("Error: Failed to extract text from PDF")
            sys.exit(1)
        
        # Create FB2 document
        print("\nCreating FB2 document...")
        root = self._create_fb2_document(text_chunks, title)
        
        # Save
        print("Saving file...")
        self._save_fb2(root)
        
        print("\n✓ Conversion completed successfully!")


def main():
    parser = argparse.ArgumentParser(
        description='Converts PDF files to FB2 format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s book.pdf
  %(prog)s book.pdf -o custom_name.fb2
  %(prog)s book.pdf -t "Book Title"
  %(prog)s book.pdf -o custom.fb2 -t "Custom Title"
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Path to input PDF file'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Path to output FB2 file (default: same name as PDF with .fb2 extension)'
    )
    
    parser.add_argument(
        '-t', '--title',
        dest='title',
        help='Book title in FB2'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0'
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.input_file):
        print(f"Error: File '{args.input_file}' not found")
        sys.exit(1)
    
    # Check extension
    if not args.input_file.lower().endswith('.pdf'):
        print("Error: Input file must have .pdf extension")
        sys.exit(1)
    
    # Perform conversion
    converter = PDFToFB2Converter(args.input_file, args.output_file)
    converter.convert(args.title)


if __name__ == '__main__':
    main()

