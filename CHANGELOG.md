# Changelog

All notable changes to QCM-AI-DevTools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-03-31

### Added
- **DevToolsWorkflow Enhancement**: Integrated Navigator and HandoffManager
  - `start_from_natural_language()`: Natural language workflow entry point
  - `validate_project()`: Project validation with release decision
  - `ai_development_with_navigation()`: AI-assisted development with navigation
  - `get_handoff_chain()`: Retrieve complete handoff chain
  - `export_handoff_chain()`: Export handoff chain as YAML/JSON
  - `_make_release_decision()`: Automated PASS/CONDITIONAL_PASS/FAIL decision
- **Release Decision Logic**: Based on quality score and failed indicators
  - PASS: score ≥80 and 0 failures
  - CONDITIONAL_PASS: score ≥70 and ≤2 failures
  - FAIL: otherwise
- **Tests**: 16 new workflow tests

### Changed
- DevToolsWorkflow now integrates Navigator by default
- DevToolsWorkflow now integrates HandoffManager by default
- Test suite expanded from 103 to 119 test cases

## [0.3.0] - 2025-03-31

### Added
- **Navigator**: Skill 00 · 智能体导航官实现
  - Intent recognition for 7 intent types
  - Confidence-based routing (≥80%/60-79%/<60%)
  - Automatic skill recommendation
  - HP-D handoff package generation
  - Tech stack extraction from natural language
  - Support for AI-enhanced mode (OpenAI API)
- **IntentType Enum**: 7 intent type classifications
- **ConfidenceLevel Enum**: 3 confidence levels
- **IntentAnalysis Dataclass**: Analysis result structure
- **Example**: `navigator_demo.py` with 8 usage examples
- **Tests**: 25 Navigator test cases

### Changed
- Updated `__init__.py` to export Navigator
- Test suite expanded from 78 to 103 test cases

## [0.2.0] - 2025-03-31

### Added
- **HandoffPackage**: Standardized handoff package compatible with ai-skill-system schema v1.1
  - Support for all 6 handoff types (HP-A through HP-F)
  - YAML/JSON serialization and deserialization
  - Validation and self-review support
  - Downstream notes for skill coordination
- **HandoffManager**: Manager for storing, retrieving, and validating handoff packages
  - In-memory storage with file persistence option
  - Chain validation and integrity checking
  - Multi-session support
  - Export/import functionality
- **Factory Functions**: Quick creation of standard handoff packages
  - `create_handoff_d()`: Route recommendation (S00 → any)
  - `create_handoff_b()`: Technology selection (S03 → S02)
  - `create_handoff_c()`: Engineering package delivery (S02 → S05)
  - `create_handoff_f()`: Validation report (S05 → release)
- **Enums**: `SkillID` and `HandoffType` for type-safe skill references
- **Example**: `handoff_demo.py` demonstrating all handoff features

### Changed
- Updated `__init__.py` to export handoff module components
- Test suite expanded from 48 to 78 test cases

### Fixed
- **BUG-001**: Fixed `extract_annotations` regex pattern
- **BUG-002**: Fixed `suggest_confidence` priority logic

## [0.1.1] - 2025-03-31

### Fixed
- **BUG-001**: Fixed `extract_annotations` regex pattern - changed character class `[结论数据引用推断]` to alternation group `(结论|数据|引用|推断)` for proper matching
- **BUG-002**: Fixed `suggest_confidence` priority logic - now checks LOW confidence patterns before HIGH, correctly handling uncertainty keywords

### Changed
- Improved confidence inference logic to prioritize uncertainty indicators

## [0.1.0] - 2025-03-31

### Added
- **ConfigGenerator**: Natural language to project configuration with intelligent inference
  - 4 project types: Research, Production, Teaching, Personal
  - Keyword-based tech stack extraction
  - Automatic scale inference
  - Configuration validation

- **TemplateGenerator**: Project scaffolding with 8 predefined templates
  - Support for all project types and scales
  - Directory structure generation
  - Configuration files creation
  - Documentation templates

- **QualityAssessor**: Multi-dimensional quality evaluation
  - CodeQualityChecker: Docstring coverage, type hints, complexity analysis
  - DocumentationChecker: Required docs verification, README quality
  - SecurityChecker: Hardcoded secrets, unsafe patterns detection

- **ConfidenceAnnotator**: AI output confidence annotation
  - 4 info types: Conclusion, Data, Citation, Inference
  - 3 confidence levels: High, Medium, Low
  - Automatic source inference
  - Batch annotation support

- **DevToolsWorkflow**: Complete workflow orchestration
  - `create_project_from_description`: End-to-end project creation
  - `ai_assisted_development_cycle`: Iterative AI development
  - `batch_create_projects`: Bulk project generation
  - `quick_start`: Simplified workflow entry

- **Shared Components**:
  - Enum types for all classifications
  - Utility functions for common operations
  - Type-safe dataclasses throughout

### Documentation
- README.md with quick start guide
- FEASIBILITY_AND_INTEGRATION.md analyzing integration possibilities
- IMPLEMENTATION_REPORT.md documenting development process
- FINAL_REPORT.md summarizing project outcomes

### Examples
- `basic_usage.py`: Core functionality demo
- `end_to_end_demo.py`: Complete workflow demonstration
- `full_workflow_demo.py`: All features showcase
- `comprehensive_demo.py`: Detailed feature usage
- `ultimate_demo.py`: Workflow orchestrator in action

### Tests
- 48 test cases covering all modules
- 95.8% pass rate
- Unit tests for all core components
- Model validation tests
- Integration tests for workflows

## [Unreleased]

### Planned
- AI API integration (OpenAI, Claude, local models)
- HandoffPackage mechanism for ai-skill-system integration
- Navigator skill implementation
- Enhanced quality assessment with 5-dimension evaluation
- Web UI interface
