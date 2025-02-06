from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

class ContentMetadata(BaseModel):
    platform: str
    content_type: str
    url: HttpUrl
    title: Optional[str] = None
    author: Optional[str] = None
    publish_time: Optional[datetime] = None
    
class AudienceAnalysis(BaseModel):
    age_distribution: Dict[str, float]
    gender_ratio: Dict[str, float]
    location_distribution: Dict[str, float]
    active_time_distribution: Dict[str, float]
    interest_tags: List[str]

class InteractionAnalysis(BaseModel):
    engagement_rate: float
    comment_sentiment: Dict[str, float]
    user_value_score: float
    follower_loyalty: float
    conversion_rate: Optional[float] = None

class CompetitorAnalysis(BaseModel):
    competitor_id: str
    competitor_name: str
    content_performance: Dict[str, float]
    audience_overlap: float
    content_strategy: Dict[str, Any]
    market_position: str

class TrendAnalysis(BaseModel):
    current_trend: str
    future_prediction: str
    growth_potential: float
    risk_factors: List[str]
    opportunity_areas: List[str]

class OptimizationSuggestions(BaseModel):
    content_optimization: Dict[str, List[str]]
    timing_suggestions: List[Dict[str, Any]]
    interaction_strategy: List[str]
    monetization_suggestions: List[str]

class ContentAnalysisResult(BaseModel):
    analysis_id: str = Field(..., description="唯一分析ID")
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: ContentMetadata
    audience_analysis: Optional[AudienceAnalysis] = None
    interaction_analysis: Optional[InteractionAnalysis] = None
    competitor_analysis: Optional[List[CompetitorAnalysis]] = None
    trend_analysis: Optional[TrendAnalysis] = None
    optimization_suggestions: Optional[OptimizationSuggestions] = None
    raw_metrics: Dict[str, Any] = Field(default_factory=dict)

class AnalysisRequest(BaseModel):
    url: HttpUrl
    analysis_type: List[str] = Field(
        default=["basic", "audience", "interaction", "competitor", "trend"],
        description="要执行的分析类型"
    )
    competitor_count: int = Field(default=3, ge=0, le=10)
    include_raw_metrics: bool = Field(default=False)

class ReportRequest(BaseModel):
    analysis_id: str
    report_format: str = Field(default="pdf")
    sections: List[str] = Field(default=["all"])
    language: str = Field(default="zh-CN")

class TeamMember(BaseModel):
    user_id: str
    username: str
    role: str
    permissions: List[str]

class Comment(BaseModel):
    comment_id: str
    user_id: str
    content: str
    created_at: datetime
    parent_id: Optional[str] = None

class Project(BaseModel):
    project_id: str
    name: str
    description: Optional[str] = None
    team_members: List[TeamMember]
    created_at: datetime
    updated_at: datetime
    analysis_ids: List[str]
    comments: List[Comment] 