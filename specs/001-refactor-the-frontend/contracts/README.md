# Component Contracts: Frontend Refactoring

This directory contains the behavioral contracts that must be preserved during refactoring.

## Contract Files

### Core Component Contracts
- `ask-component.md` - Chat/Q&A interface behavior
- `repository-page.md` - Main repository page functionality  
- `mermaid-component.md` - Diagram rendering behavior
- `user-selector.md` - Model selection interface

### Supporting Contracts
- `home-page.md` - Landing page behavior
- `slides-page.md` - Presentation mode functionality
- `workshop-page.md` - Workshop interface behavior

## Contract Validation

Each contract file includes:
1. **Public API** - Props, methods, events that must be preserved
2. **Behavior Specifications** - How the component should respond to interactions
3. **State Management** - Internal state that affects external behavior
4. **Integration Points** - How the component interacts with other parts of the system
5. **Test Scenarios** - Specific cases that must continue to work

## Usage

These contracts serve as:
- **Refactoring Guidelines** - What must be preserved during code changes
- **Test Requirements** - Behaviors that must be validated
- **API Documentation** - Public interface definitions
- **Regression Prevention** - Catching unintended changes
