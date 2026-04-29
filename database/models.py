TABLE_ANALYSES = 'analyses'
TABLE_STATISTICS = 'statistics'

COLUMNS_ANALYSES = (
    'id',
    'email_text',
    'email_preview',
    'result',
    'is_phishing',
    'confidence',
    'analyzed_at',
)

COLUMNS_STATISTICS = (
    'id',
    'total_analyzed',
    'total_phishing',
    'total_legitimate',
    'last_updated',
)
