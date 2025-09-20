# CO2-Aware Shopping Assistant - Critical Issues TODO List

## 🚨 Critical Issues to Fix

### 1. Product Discovery Agent Errors ❌
- [ ] **Issue**: "show all products" returns "I encountered an error while searching for products. Please try again."
- [ ] **Issue**: "find watch" returns "I encountered an error while searching for products. Please try again."
- [ ] **Root Cause**: gRPC connection to Online Boutique product catalog service failing
- [ ] **Fix**: Ensure protobuf files are properly deployed and gRPC connection works

### 2. CO2 State Management Issues ❌
- [ ] **Issue**: Double-counting shipping CO2 in header badge
- [ ] **Issue**: Persistent shipping CO2 state across operations
- [ ] **Issue**: Inconsistent CO2 value sources (Product vs Total vs Cart)
- [ ] **Issue**: Incorrect reset behavior after "what's in my cart"

### 3. UI State Synchronization Issues ❌
- [ ] **Issue**: Header badge shows wrong values compared to chat responses
- [ ] **Issue**: Shipping CO2 not updating when new shipping method selected
- [ ] **Issue**: Product CO2 sometimes shows total CO2 instead of just product CO2

### 4. CO2 Calculation Logic Issues ❌
- [ ] **Issue**: Total CO2 = (Product CO2 + Shipping CO2) + Shipping CO2 (double-counting)
- [ ] **Issue**: Expected: Product CO2 + Shipping CO2 = Total CO2
- [ ] **Issue**: Actual: (Product CO2 + Shipping CO2) + Shipping CO2 = Total CO2

## 🔧 Implementation Plan

### Phase 1: Fix Product Discovery Agent (Priority: HIGH)
1. [ ] Rebuild Docker image with protobuf files
2. [ ] Deploy updated image to Kubernetes
3. [ ] Test gRPC connection to Online Boutique
4. [ ] Verify "show all products" and "find watch" work

### Phase 2: Fix CO2 State Management (Priority: HIGH)
1. [ ] Fix double-counting shipping CO2 in header badge
2. [ ] Implement proper shipping CO2 reset logic
3. [ ] Fix product CO2 vs total CO2 display logic
4. [ ] Implement correct reset behavior

### Phase 3: Fix UI State Synchronization (Priority: MEDIUM)
1. [ ] Synchronize header badge with chat responses
2. [ ] Fix shipping CO2 updates when new method selected
3. [ ] Ensure consistent CO2 values across all UI components

### Phase 4: Testing and Validation (Priority: HIGH)
1. [ ] Test complete flow: show all products → find watch → add to cart → eco shipping → payment
2. [ ] Test complete flow: add sunglasses → checkout with ground → what's in my cart → payment
3. [ ] Verify CO2 calculations are correct in all scenarios
4. [ ] Verify UI state synchronization works properly

## 🎯 Success Criteria
- [ ] "show all products" returns real products from Online Boutique with AI-powered responses
- [ ] "find watch" returns real watch products from Online Boutique with AI-powered responses
- [ ] CO2 calculations are accurate and consistent across all UI components
- [ ] Header badge shows correct values that match chat responses
- [ ] Shipping CO2 updates correctly when new shipping method selected
- [ ] Badge resets appropriately (after payment success, after cart clear)
- [ ] Badge does NOT reset inappropriately (after "what's in my cart", after adding products)

## 📝 Notes
- Focus on systematic fixes, one issue at a time
- Test each fix thoroughly before moving to next
- Maintain backward compatibility where possible
- Document all changes for future reference
