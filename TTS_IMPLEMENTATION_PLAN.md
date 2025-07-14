# Technical Implementation: Multi-Provider TTS Integration
## LearnOnTheGo Phase 2f Enhancement

**Date:** July 14, 2025  
**Target:** Existing authentication-enabled application  
**Approach:** Enhance without rebuilding

---

## 🏗️ **Architecture Enhancement Design**

### **Current System Integration Points**
```
Existing Flow:
User Authentication ✅ → API Key Management ✅ → Lecture Generation → TTS Provider Selection ⭐ NEW

Enhanced Flow:
User → Settings → Provider Preferences → Lecture Creation → Smart Provider Selection → Cost-Optimized Generation
```

---

## 💾 **Database Schema Extensions**

### **New Tables Required**

```sql
-- TTS Provider configurations
CREATE TABLE tts_providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    cost_per_million_chars DECIMAL(10,2),
    quality_tier VARCHAR(20), -- 'free', 'premium', 'ultimate'
    languages JSON, -- ['en', 'es', 'fr', ...]
    features JSON, -- {'voice_cloning': true, 'speed_control': true}
    api_endpoint VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User TTS preferences
CREATE TABLE user_tts_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    preferred_provider VARCHAR(50) REFERENCES tts_providers(name),
    fallback_provider VARCHAR(50) REFERENCES tts_providers(name),
    quality_preference VARCHAR(20) DEFAULT 'balanced', -- 'cost', 'balanced', 'quality'
    max_cost_per_lecture DECIMAL(8,2) DEFAULT 5.00,
    voice_settings JSON, -- Provider-specific voice configs
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- TTS usage tracking per provider
CREATE TABLE tts_usage_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    lecture_id INTEGER REFERENCES lectures(id) ON DELETE CASCADE,
    provider_name VARCHAR(50) REFERENCES tts_providers(name),
    characters_processed INTEGER NOT NULL,
    cost_usd DECIMAL(8,4),
    processing_time_ms INTEGER,
    quality_rating INTEGER CHECK (quality_rating >= 1 AND quality_rating <= 5),
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **Enhanced Lecture Model**
```sql
-- Add to existing lectures table
ALTER TABLE lectures ADD COLUMN tts_provider_used VARCHAR(50);
ALTER TABLE lectures ADD COLUMN tts_cost_usd DECIMAL(8,4);
ALTER TABLE lectures ADD COLUMN voice_quality_rating INTEGER;
ALTER TABLE lectures ADD COLUMN tts_processing_time_ms INTEGER;
```

---

## 🔧 **Service Layer Architecture**

### **1. Enhanced TTS Provider Service**

```python
# backend/services/tts_provider_service.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TTSQualityTier(Enum):
    FREE = "free"
    PREMIUM = "premium" 
    ULTIMATE = "ultimate"

@dataclass
class TTSProviderConfig:
    name: str
    display_name: str
    cost_per_million_chars: float
    quality_tier: TTSQualityTier
    languages: List[str]
    features: Dict[str, bool]
    api_key_required: bool

class BaseTTSProvider(ABC):
    """Abstract base class for TTS providers"""
    
    @abstractmethod
    async def synthesize(self, text: str, voice_config: Dict) -> Tuple[bytes, Dict]:
        """Return audio bytes and metadata"""
        pass
    
    @abstractmethod
    def calculate_cost(self, text: str) -> float:
        """Calculate cost for given text"""
        pass
    
    @abstractmethod
    def get_available_voices(self, language: str = 'en') -> List[Dict]:
        """Get available voices for language"""
        pass

class GoogleStandardTTS(BaseTTSProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.cost_per_million = 4.0
    
    async def synthesize(self, text: str, voice_config: Dict) -> Tuple[bytes, Dict]:
        # Google TTS implementation
        pass
    
    def calculate_cost(self, text: str) -> float:
        chars = len(text)
        if chars <= 4_000_000:  # Free tier
            return 0.0
        return ((chars - 4_000_000) / 1_000_000) * self.cost_per_million

class OpenAITTS(BaseTTSProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.cost_per_thousand = 0.015  # Standard model
    
    async def synthesize(self, text: str, voice_config: Dict) -> Tuple[bytes, Dict]:
        # OpenAI TTS implementation
        pass
    
    def calculate_cost(self, text: str) -> float:
        chars = len(text)
        return (chars / 1000) * self.cost_per_thousand

class TTSProviderManager:
    """Manages multiple TTS providers and smart selection"""
    
    def __init__(self):
        self.providers: Dict[str, BaseTTSProvider] = {}
        self.provider_configs: Dict[str, TTSProviderConfig] = {}
    
    def register_provider(self, name: str, provider: BaseTTSProvider, config: TTSProviderConfig):
        self.providers[name] = provider
        self.provider_configs[name] = config
    
    async def get_optimal_provider(
        self, 
        user_preferences: Dict, 
        text: str, 
        language: str = 'en'
    ) -> str:
        """Select optimal provider based on user preferences and content"""
        
        quality_pref = user_preferences.get('quality_preference', 'balanced')
        max_cost = user_preferences.get('max_cost_per_lecture', 5.0)
        preferred_provider = user_preferences.get('preferred_provider')
        
        # Calculate costs for each available provider
        options = []
        for name, provider in self.providers.items():
            config = self.provider_configs[name]
            if language not in config.languages:
                continue
                
            cost = provider.calculate_cost(text)
            if cost > max_cost:
                continue
                
            options.append({
                'name': name,
                'cost': cost,
                'quality_tier': config.quality_tier,
                'config': config
            })
        
        # Sort by preference
        if quality_pref == 'cost':
            options.sort(key=lambda x: x['cost'])
        elif quality_pref == 'quality':
            tier_order = {'ultimate': 3, 'premium': 2, 'free': 1}
            options.sort(key=lambda x: tier_order[x['quality_tier'].value], reverse=True)
        else:  # balanced
            # Weight cost and quality
            for opt in options:
                tier_score = {'ultimate': 3, 'premium': 2, 'free': 1}[opt['quality_tier'].value]
                cost_score = 1 / (opt['cost'] + 0.01)  # Avoid division by zero
                opt['balanced_score'] = tier_score * cost_score
            options.sort(key=lambda x: x['balanced_score'], reverse=True)
        
        # Return preferred provider if available and within constraints
        if preferred_provider and any(opt['name'] == preferred_provider for opt in options):
            return preferred_provider
        
        return options[0]['name'] if options else 'google_standard'  # fallback
```

### **2. Cost Calculation Service**

```python
# backend/services/cost_calculation_service.py
class CostCalculationService:
    """Real-time cost calculation and budgeting"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def estimate_lecture_cost(
        self, 
        text: str, 
        provider_name: str,
        user_id: int
    ) -> Dict:
        """Estimate cost for lecture generation"""
        
        provider_manager = get_tts_provider_manager()
        provider = provider_manager.providers[provider_name]
        config = provider_manager.provider_configs[provider_name]
        
        estimated_cost = provider.calculate_cost(text)
        
        # Get user's monthly usage
        monthly_usage = await self.get_monthly_usage(user_id)
        
        return {
            'estimated_cost_usd': estimated_cost,
            'provider_name': provider_name,
            'provider_display_name': config.display_name,
            'quality_tier': config.quality_tier.value,
            'character_count': len(text),
            'monthly_usage_usd': monthly_usage,
            'cost_breakdown': {
                'base_cost': estimated_cost,
                'free_tier_savings': max(0, provider.calculate_free_tier_savings(text)),
                'effective_cost': estimated_cost
            }
        }
    
    async def track_usage(
        self,
        user_id: int,
        lecture_id: int,
        provider_name: str,
        characters_processed: int,
        actual_cost: float,
        processing_time_ms: int,
        success: bool = True,
        error_message: str = None
    ):
        """Track actual TTS usage"""
        
        usage_log = TTSUsageLog(
            user_id=user_id,
            lecture_id=lecture_id,
            provider_name=provider_name,
            characters_processed=characters_processed,
            cost_usd=actual_cost,
            processing_time_ms=processing_time_ms,
            success=success,
            error_message=error_message
        )
        
        self.db.add(usage_log)
        self.db.commit()
        
        # Update user's monthly totals
        await self.update_monthly_totals(user_id)
```

---

## 🎨 **Frontend Integration**

### **1. Provider Selection Component**

```typescript
// frontend/src/components/TTSProviderSelector.tsx
interface TTSProvider {
  name: string;
  displayName: string;
  costPerMillionChars: number;
  qualityTier: 'free' | 'premium' | 'ultimate';
  estimatedCost: number;
  features: string[];
}

export const TTSProviderSelector: React.FC = () => {
  const [providers, setProviders] = useState<TTSProvider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('google_standard');
  const [textLength, setTextLength] = useState<number>(0);
  
  useEffect(() => {
    // Fetch available providers and calculate costs
    fetchProviders();
  }, [textLength]);
  
  const handleProviderSelect = (providerName: string) => {
    setSelectedProvider(providerName);
    // Update parent component with selection
  };
  
  return (
    <div className="tts-provider-selector">
      <h3>Choose Voice Quality & Provider</h3>
      
      {providers.map(provider => (
        <div 
          key={provider.name}
          className={`provider-option ${selectedProvider === provider.name ? 'selected' : ''}`}
          onClick={() => handleProviderSelect(provider.name)}
        >
          <div className="provider-header">
            <span className="provider-name">{provider.displayName}</span>
            <span className={`quality-badge ${provider.qualityTier}`}>
              {provider.qualityTier.toUpperCase()}
            </span>
          </div>
          
          <div className="cost-info">
            <span className="cost">
              ${provider.estimatedCost.toFixed(3)} for this lecture
            </span>
            <span className="cost-detail">
              (${provider.costPerMillionChars}/million chars)
            </span>
          </div>
          
          <div className="features">
            {provider.features.map(feature => (
              <span key={feature} className="feature-tag">{feature}</span>
            ))}
          </div>
          
          <button className="play-sample">🔊 Play Voice Sample</button>
        </div>
      ))}
      
      <div className="cost-summary">
        <strong>Total Estimated Cost: ${providers.find(p => p.name === selectedProvider)?.estimatedCost.toFixed(3)}</strong>
      </div>
    </div>
  );
};
```

### **2. Enhanced Lecture Creation Flow**

```typescript
// frontend/src/screens/CreateLectureScreen.tsx
export const CreateLectureScreen: React.FC = () => {
  const [step, setStep] = useState(1);
  const [lectureData, setLectureData] = useState({
    topic: '',
    duration: 15,
    difficulty: 'intermediate',
    ttsProvider: 'google_standard',
    voiceConfig: {}
  });
  
  const renderStepContent = () => {
    switch(step) {
      case 1:
        return <TopicInputComponent />;
      case 2:
        return <DurationDifficultyComponent />;
      case 3:
        return <TTSProviderSelector 
          textLength={lectureData.topic.length}
          onProviderSelect={(provider) => 
            setLectureData({...lectureData, ttsProvider: provider})
          }
        />;
      case 4:
        return <ReviewAndGenerateComponent />;
    }
  };
  
  return (
    <div className="create-lecture-screen">
      <div className="progress-bar">
        <div className={`step ${step >= 1 ? 'completed' : ''}`}>Content</div>
        <div className={`step ${step >= 2 ? 'completed' : ''}`}>Settings</div>
        <div className={`step ${step >= 3 ? 'completed' : ''}`}>Voice</div>
        <div className={`step ${step >= 4 ? 'completed' : ''}`}>Generate</div>
      </div>
      
      {renderStepContent()}
      
      <div className="navigation-buttons">
        {step > 1 && (
          <button onClick={() => setStep(step - 1)}>Previous</button>
        )}
        {step < 4 && (
          <button onClick={() => setStep(step + 1)}>Next</button>
        )}
        {step === 4 && (
          <button onClick={generateLecture}>Generate Lecture</button>
        )}
      </div>
    </div>
  );
};
```

---

## 📡 **API Endpoints Enhancement**

### **New Endpoints Required**

```python
# backend/api/tts_provider_routes.py
@router.get("/providers", response_model=List[Dict[str, Any]])
async def list_available_providers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available TTS providers with cost estimates"""
    pass

@router.post("/providers/estimate-cost")
async def estimate_provider_costs(
    text: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get cost estimates for all providers for given text"""
    pass

@router.get("/preferences")
async def get_user_tts_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's TTS provider preferences"""
    pass

@router.put("/preferences")
async def update_user_tts_preferences(
    preferences: TTSPreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's TTS provider preferences"""
    pass

@router.get("/usage/monthly")
async def get_monthly_tts_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's monthly TTS usage and costs by provider"""
    pass
```

---

## 🔄 **Migration & Rollout Strategy**

### **Phase 1: Foundation (Week 1)**
1. **Database migrations** - Add new tables
2. **Basic provider implementations** - Google Standard + OpenAI
3. **Provider selection UI** - Simple dropdown
4. **Cost calculation engine** - Real-time estimates

### **Phase 2: Enhancement (Week 2)**  
1. **Smart provider recommendation** - Based on user preferences
2. **Advanced UI components** - Voice samples, quality comparison
3. **Usage tracking** - Detailed analytics
4. **A/B testing framework** - Provider performance comparison

### **Phase 3: Optimization (Week 3-4)**
1. **Machine learning recommendations** - Usage pattern analysis
2. **Advanced features** - Custom voice training preparation
3. **Performance optimization** - Caching, batch processing
4. **User onboarding** - Provider selection guidance

---

## 📊 **Implementation Priority Matrix**

| Feature | Impact | Effort | Priority | Timeline |
|---------|--------|--------|----------|----------|
| Google Standard TTS | High | Low | 🔴 P0 | Week 1 |
| OpenAI TTS Integration | High | Medium | 🔴 P0 | Week 1 |
| Provider Selection UI | High | Medium | 🟡 P1 | Week 1 |
| Cost Calculation | High | Low | 🔴 P0 | Week 1 |
| Usage Tracking | Medium | Low | 🟡 P1 | Week 2 |
| Smart Recommendations | Medium | High | 🟢 P2 | Week 3 |
| Voice Samples | Low | Medium | 🟢 P2 | Week 4 |

---

**This technical implementation plan provides a clear roadmap for enhancing LearnOnTheGo with multi-provider TTS capabilities while maintaining the existing authentication and core functionality. The phased approach ensures minimal disruption while maximizing cost savings and user experience improvements.**
