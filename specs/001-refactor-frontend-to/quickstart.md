# Quickstart: Quick Access Ask UI from Home Page

## Prerequisites
- Node.js 20+ installed
- DeepWiki project running locally
- At least one repository processed in the system

## Quick Validation Steps

### 1. Feature Access Test
**Goal**: Verify Ask UI is accessible from home page

**Steps**:
1. Navigate to DeepWiki home page (`http://localhost:3000`)
2. Look for Ask UI section below the repository input form
3. Verify Ask UI section is visible and renders correctly

**Expected Result**: Ask UI section appears with repository selection interface

**Success Criteria**: ✅ Ask section visible, ✅ No console errors, ✅ Repository selector rendered

### 2. Repository Selection Test
**Goal**: Verify repository selection functionality

**Steps**:
1. Click on repository selector dropdown
2. Select a previously processed repository
3. Verify repository appears as selected
4. Try manual URL input with a new repository URL

**Expected Result**: Repository selection updates Ask UI context

**Success Criteria**: ✅ Dropdown shows repositories, ✅ Selection updates state, ✅ Manual input accepted

### 3. Multi-Repository Mode Test
**Goal**: Verify multi-repository functionality

**Steps**:
1. Toggle multi-repository mode switch
2. Select multiple repositories from the list
3. Verify all selected repositories are displayed
4. Remove one repository and verify it's removed from selection

**Expected Result**: Multi-repository selection works correctly

**Success Criteria**: ✅ Toggle switches modes, ✅ Multiple selection works, ✅ Removal works

### 4. Ask Functionality Test
**Goal**: Verify Ask UI works with repository context

**Steps**:
1. Select a repository (single or multiple)
2. Type a question in the Ask input field
3. Submit the question
4. Wait for AI response
5. Verify response is relevant to selected repository/repositories

**Expected Result**: Ask UI functions normally with repository context

**Success Criteria**: ✅ Question submitted, ✅ Response received, ✅ No errors in console

### 5. Integration Test
**Goal**: Verify integration with existing home page functionality

**Steps**:
1. Use repository input form to generate a wiki (existing functionality)
2. Navigate back to home page
3. Use Ask UI to query the same repository
4. Verify both functionalities work independently

**Expected Result**: No interference between existing and new functionality

**Success Criteria**: ✅ Wiki generation works, ✅ Ask UI works, ✅ No conflicts

### 6. Error Handling Test
**Goal**: Verify graceful error handling

**Steps**:
1. Try to ask a question without selecting any repository
2. Select an invalid/non-existent repository URL
3. Test with network disconnected (if possible)
4. Verify appropriate error messages are shown

**Expected Result**: Errors are handled gracefully with user-friendly messages

**Success Criteria**: ✅ Validation errors shown, ✅ Network errors handled, ✅ No crashes

## Development Setup

### Running Tests
```bash
# Install dependencies (if not already done)
npm install

# Run component tests for new HomePageAsk component
npm test src/components/HomePageAsk.test.tsx

# Run integration tests for home page modifications
npm test src/app/page.test.tsx

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch
```

### Local Development
```bash
# Start development server
npm run dev

# Open browser to http://localhost:3000
# Navigate to home page to test the feature

# Start backend server (if needed for Ask functionality)
python -m backend.main
```

### Component Development Files
```bash
# Create new component and test files
touch src/components/HomePageAsk.tsx
touch src/components/HomePageAsk.test.tsx

# The main integration will be in existing files:
# src/app/page.tsx (modify existing)
# src/app/page.test.tsx (add tests if doesn't exist)
```

## Troubleshooting

### Common Issues

**Ask UI not appearing on home page**
- Check console for React errors
- Verify HomePageAsk component is imported and rendered
- Check if component is conditionally hidden

**Repository selection not working**
- Verify projects data is being passed correctly
- Check RepositorySelector component integration
- Verify state management in HomePageAsk component

**Ask functionality not working**
- Check repository context passed to Ask component
- Verify authentication state is correct
- Check network requests in browser dev tools

**Multi-repository mode issues**
- Verify MultiRepositorySelector component integration
- Check repository array state management
- Verify Ask component handles multiple repositories

### Debug Commands
```bash
# Check component state in browser dev tools
console.log('HomePageAsk state:', componentState);

# Verify repository context
console.log('Repository context:', repoContext);

# Check Ask component props
console.log('Ask props:', askProps);
```

## Performance Validation

### Expected Performance Metrics
- Initial page load: < 2 seconds
- Repository selection response: < 100ms
- Ask UI render time: < 50ms
- Question submission: < 500ms to API

### Performance Testing
```bash
# Run Lighthouse audit
npx lighthouse http://localhost:3000 --view

# Check bundle size impact
npm run build
npm run analyze
```

## Success Checklist

### Functional Requirements
- [ ] Ask UI accessible from home page
- [ ] Repository selection works (single and multi)
- [ ] Ask functionality works with repository context
- [ ] Multi-repository support functional
- [ ] Error handling works gracefully
- [ ] No breaking changes to existing functionality

### Non-Functional Requirements
- [ ] Performance requirements met
- [ ] Responsive design maintained
- [ ] Accessibility standards met
- [ ] Browser compatibility maintained
- [ ] Console errors minimal/none

### Integration Requirements
- [ ] Home page layout not disrupted
- [ ] Existing Ask functionality unchanged
- [ ] Repository selector components reused
- [ ] Authentication flow preserved
- [ ] Theme and styling consistent

## Deployment Checklist

### Pre-deployment
- [ ] All tests passing
- [ ] Performance metrics validated
- [ ] Cross-browser testing completed
- [ ] Responsive design verified
- [ ] Error scenarios tested

### Post-deployment
- [ ] Feature flagging configured (if applicable)
- [ ] Monitoring alerts configured
- [ ] User feedback collection ready
- [ ] Rollback plan prepared
- [ ] Documentation updated
