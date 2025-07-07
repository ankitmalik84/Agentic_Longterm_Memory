from typing import Dict, Any, TypedDict, List, Optional, Literal, Union

# Content types
NotionContentType = Literal[
    "paragraph",
    "heading_1",
    "heading_2",
    "heading_3",
    "bulleted_list_item",
    "to_do",
    "bookmark",
    "link_to_page"
]

# Analytics types
AnalyticsType = Literal["workspace", "content", "activity", "database"]

# Bulk operation types
BulkOperationType = Literal["list", "list_pages", "analyze", "analyze_pages"]

# Agent action types
AgentActionType = Literal[
    "search",
    "read_page",
    "create_page",
    "add_content",
    "bulk_add_content",
    "analytics",
    "bulk_operations"
]

# Search Types
class NotionSearchResult(TypedDict):
    id: str
    object: str
    created_time: str
    last_edited_time: str
    url: str
    title: str

class NotionSearchResponse(TypedDict):
    success: bool
    data: Dict[str, Any]
    message: str
    timestamp: str

# Page Types
class NotionPageContent(TypedDict):
    id: str
    type: str
    created_time: str
    last_edited_time: str
    text: str
    has_children: bool

class NotionPageProperties(TypedDict):
    title: Dict[str, Any]  # Complex nested structure for title

class NotionPageData(TypedDict):
    id: str
    title: str
    created_time: str
    last_edited_time: str
    url: str
    properties: NotionPageProperties
    content: List[NotionPageContent]

class NotionPageResponse(TypedDict):
    success: bool
    data: NotionPageData
    message: str
    timestamp: str

# Create Page Types
class NotionCreatePageData(TypedDict):
    id: str
    title: str
    url: str
    created_time: str
    parent_id: str
    content_blocks_created: int

class NotionCreatePageResponse(TypedDict):
    success: bool
    data: NotionCreatePageData
    message: str
    timestamp: str

# Content Addition Types
class NotionAddContentData(TypedDict):
    page_id: str
    content_type: str
    blocks_added: int
    block_ids: List[str]

class NotionAddContentResponse(TypedDict):
    success: bool
    data: NotionAddContentData
    message: str
    timestamp: str

class NotionContentItem(TypedDict, total=False):
    content_type: NotionContentType
    content: str
    checked: bool  # Optional for to_do items
    url: str  # Optional for bookmark and link_to_page
    page_reference: str  # Optional for link_to_page


class NotionBulkAddContentData(TypedDict):
    page_id: str
    items_processed: int
    blocks_added: int
    block_ids: List[str]

class NotionBulkAddContentResponse(TypedDict):
    success: bool
    data: NotionBulkAddContentData
    message: str
    timestamp: str

# Analytics Types
class NotionRecentPage(TypedDict):
    title: str
    last_edited: str
    id: str

class NotionAnalyticsData(TypedDict):
    type: AnalyticsType
    total_pages: int
    total_databases: int
    recent_activity_7_days: int
    recent_pages: List[NotionRecentPage]
    timestamp: str

class NotionAnalyticsResponse(TypedDict):
    success: bool
    data: NotionAnalyticsData
    message: str
    timestamp: str

# Bulk Operation Types
class NotionPageInfo(TypedDict):
    id: str
    title: str
    created_time: str
    last_edited_time: str
    url: str
    block_count: Union[int, str]  # can be int or "not_calculated"

class NotionPaginationInfo(TypedDict):
    limit_applied: int
    include_block_counts: bool
    note: str

class NotionBulkListData(TypedDict):
    operation: str
    total: int
    returned: int
    pages: List[NotionPageInfo]
    pagination_info: NotionPaginationInfo
    timestamp: str

class NotionBulkResponse(TypedDict):
    success: bool
    data: NotionBulkListData
    message: str
    timestamp: str

class BulkOperationQuery(TypedDict, total=False):
    limit: int
    include_block_counts: bool

# Agent Query Types
class AgentQueryParameters(TypedDict, total=False):
    # Search parameters
    query: str
    page_size: int
    # Analytics parameters
    type: str
    # Bulk operations parameters
    operation: str
    # Other parameters
    identifier: str  # for read_page
    title: str  # for create_page
    content: str  # for add_content
    parent_id: str  # for create_page
    items: List[Dict[str, Any]]  # for bulk_add_content

class AgentQuery(TypedDict):
    action: AgentActionType
    parameters: AgentQueryParameters

class AgentQueryResponse(TypedDict):
    success: bool
    data: Dict[str, Any]  # Response data varies by action
    message: str
    timestamp: str 