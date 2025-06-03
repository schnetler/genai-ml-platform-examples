"""Parser for Knowledge Base results that handles chunked documents."""

import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class KBDocumentParser:
    """Parses Knowledge Base documents that may be chunked."""
    
    @staticmethod
    def parse_destination_from_chunks(chunks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Parse destination information from potentially multiple chunks.
        
        Args:
            chunks: List of KB result chunks
            
        Returns:
            Parsed destination data or None
        """
        destination_data = {}
        metadata_found = False
        
        for chunk in chunks:
            content = chunk.get('content', {})
            text = content.get('text', '')
            
            # Skip empty chunks
            if not text.strip():
                continue
                
            # Try to extract information from the chunk
            if text.strip().startswith('{'):
                # This might be a JSON chunk
                try:
                    # First, check if it's a complete JSON document
                    if '"documentId"' in text and '"metadata"' in text:
                        # This looks like a complete document
                        doc_data = json.loads(text)
                        metadata = doc_data.get('metadata', {})
                        if metadata:
                            destination_data.update({
                                'code': metadata.get('code', ''),
                                'name': metadata.get('name', ''),
                                'country': metadata.get('country', ''),
                                'tags': metadata.get('tags', []),
                                'latitude': metadata.get('latitude'),
                                'longitude': metadata.get('longitude'),
                                'continent': metadata.get('continent', '')
                            })
                            metadata_found = True
                            
                        # Extract description from content
                        content_text = doc_data.get('content', {}).get('text', '')
                        if content_text:
                            destination_data['content_text'] = content_text
                            
                except json.JSONDecodeError:
                    # Partial JSON, skip
                    logger.debug("Skipping partial JSON chunk")
                    
            elif '## Overview' in text:
                # This is a content chunk with overview
                overview_start = text.find('## Overview') + len('## Overview')
                overview_end = text.find('\n\n##', overview_start)
                if overview_end == -1:
                    overview_end = text.find('\n\n', overview_start)
                    if overview_end == -1:
                        overview_end = len(text)
                description = text[overview_start:overview_end].strip()
                if description:
                    destination_data['description'] = description
                    
            elif '## Top Attractions' in text:
                # This is a content chunk with attractions
                attr_start = text.find('## Top Attractions') + len('## Top Attractions')
                attr_end = text.find('\n\n##', attr_start)
                if attr_end == -1:
                    attr_end = len(text)
                attractions_text = text[attr_start:attr_end].strip()
                attractions = [line.strip('- ').strip() for line in attractions_text.split('\n') 
                             if line.strip().startswith('-')]
                if attractions:
                    destination_data['attractions'] = attractions
                    destination_data['activities'] = attractions
                    
            elif '## Travel Style Tags' in text:
                # Extract tags from content
                tags_start = text.find('## Travel Style Tags') + len('## Travel Style Tags')
                tags_end = text.find('\n\n##', tags_start)
                if tags_end == -1:
                    tags_end = text.find('\n\n', tags_start)
                    if tags_end == -1:
                        tags_end = len(text)
                tags_text = text[tags_start:tags_end].strip()
                if tags_text and ', ' in tags_text:
                    tags = [tag.strip() for tag in tags_text.split(', ')]
                    destination_data['tags'] = tags
                    
            # Try to extract location info from chunk URI
            location = chunk.get('location', {})
            s3_location = location.get('s3Location', {})
            uri = s3_location.get('uri', '')
            
            # Extract destination code from URI if we don't have it
            if not destination_data.get('code') and '/destinations/' in uri:
                # URI format: .../destinations/cdg.json
                filename = uri.split('/')[-1]
                if filename.endswith('.json'):
                    code = filename[:-5].upper()
                    destination_data['code'] = code
                    
                    # If we don't have a name, try to infer it
                    if not destination_data.get('name'):
                        code_to_name = {
                            'CDG': 'Paris',
                            'FCO': 'Rome',
                            'VCE': 'Venice',
                            'DPS': 'Bali',
                            'NYC': 'New York',
                            'NRT': 'Tokyo',
                            'SYD': 'Sydney',
                            'CPT': 'Cape Town',
                            'GIG': 'Rio de Janeiro'
                        }
                        if code in code_to_name:
                            destination_data['name'] = code_to_name[code]
                            
        # Parse content_text if we have it
        if 'content_text' in destination_data:
            content_text = destination_data['content_text']
            
            if not destination_data.get('description') and '## Overview' in content_text:
                overview_start = content_text.find('## Overview') + len('## Overview')
                overview_end = content_text.find('\n\n##', overview_start)
                if overview_end == -1:
                    overview_end = content_text.find('\n\n', overview_start)
                description = content_text[overview_start:overview_end].strip()
                if description:
                    destination_data['description'] = description
                    
            if not destination_data.get('attractions') and '## Top Attractions' in content_text:
                attr_start = content_text.find('## Top Attractions') + len('## Top Attractions')
                attr_end = content_text.find('\n\n##', attr_start)
                if attr_end == -1:
                    attr_end = len(content_text)
                attractions_text = content_text[attr_start:attr_end].strip()
                attractions = [line.strip('- ').strip() for line in attractions_text.split('\n') 
                             if line.strip().startswith('-')]
                if attractions:
                    destination_data['attractions'] = attractions
                    destination_data['activities'] = attractions
                    
            # Remove content_text from final result
            destination_data.pop('content_text', None)
            
        # Only return if we have at least a name
        if destination_data.get('name'):
            return destination_data
            
        return None