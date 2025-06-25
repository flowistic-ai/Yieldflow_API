#!/usr/bin/env python3
"""
Comprehensive Template Validator for AI Investment Assistant
Tests all question templates for accuracy, financial modeling, and UX
"""

import asyncio
import json
import time
from typing import Dict, List, Any
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.live_investment_assistant import LiveInvestmentAssistant

class TemplateValidator:
    def __init__(self):
        self.assistant = LiveInvestmentAssistant()
        self.test_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'test_details': [],
            'performance_metrics': {},
            'financial_accuracy': {}
        }
    
    async def run_comprehensive_validation(self):
        """Run all validation tests"""
        print("🚀 Comprehensive AI Investment Assistant Template Validation")
        print("=" * 70)
        
        # Define test cases for all templates
        test_cases = [
            # Investment Guidance Templates
            {
                'category': 'Investment Guidance',
                'template': 'Income Target Planning',
                'queries': [
                    'I have $2997 and want to earn $10 monthly',  # 4% realistic
                    'I have $5000 and want to earn $25 monthly',  # 6% realistic
                    'I have $1000 and want to earn $50 monthly',  # 60% unrealistic
                    'I have $10000 and want to earn $30 monthly', # 3.6% conservative
                ],
                'expected_response_type': 'investment_reality_check',
                'financial_validation': True
            },
            
            # Stock Screening Templates
            {
                'category': 'Stock Screening',
                'template': 'Dividend Yield Screening',
                'queries': [
                    'Find dividend stocks with yield above 4%',
                    'Find dividend stocks with yield above 6%',
                    'Find dividend stocks with yield above 2%'
                ],
                'expected_response_type': 'screening_results',
                'financial_validation': False
            },
            {
                'category': 'Stock Screening',
                'template': 'Sector + P/E Screening',
                'queries': [
                    'Show Technology stocks with P/E below 20',
                    'Show Utilities stocks with P/E below 15',
                    'Show Healthcare stocks with P/E below 25'
                ],
                'expected_response_type': 'screening_results',
                'financial_validation': False
            },
            {
                'category': 'Stock Screening',
                'template': 'Price + Yield Screening',
                'queries': [
                    'Find stocks under $100 with yield above 3%',
                    'Find stocks under $50 with yield above 4%',
                    'Find stocks under $200 with yield above 2.5%'
                ],
                'expected_response_type': 'screening_results',
                'financial_validation': False
            },
            
            # Stock Analysis Templates
            {
                'category': 'Stock Analysis',
                'template': 'Multi-Stock Analysis',
                'queries': [
                    'Analyze KO PEP dividend quality',
                    'Analyze JNJ PFE MRK dividend quality',
                    'Analyze VZ T dividend quality'
                ],
                'expected_response_type': 'analysis_results',
                'financial_validation': False
            },
            {
                'category': 'Stock Analysis',
                'template': 'Single Stock Analysis',
                'queries': [
                    'Evaluate AAPL dividend sustainability',
                    'Evaluate JNJ dividend sustainability',
                    'Evaluate O dividend sustainability'
                ],
                'expected_response_type': 'analysis_results',
                'financial_validation': False
            }
        ]
        
        for test_case in test_cases:
            await self._test_template_category(test_case)
        
        await self._test_financial_accuracy()
        await self._test_performance_benchmarks()
        await self._generate_comprehensive_report()
    
    async def _test_template_category(self, test_case: Dict[str, Any]):
        """Test a specific template category"""
        category = test_case['category']
        template = test_case['template']
        
        print(f"\n📋 Testing {category} - {template}")
        print("-" * 50)
        
        for i, query in enumerate(test_case['queries'], 1):
            print(f"\n🔍 Test {i}: {query}")
            
            start_time = time.time()
            try:
                result = await self.assistant.process_query(query)
                processing_time = time.time() - start_time
                
                # Validate response structure
                validation_results = self._validate_response(
                    result, 
                    test_case['expected_response_type'],
                    test_case.get('financial_validation', False),
                    query
                )
                
                # Record results
                test_result = {
                    'category': category,
                    'template': template,
                    'query': query,
                    'success': result.success,
                    'processing_time': processing_time,
                    'response_type': test_case['expected_response_type'],
                    'validation_passed': validation_results['passed'],
                    'validation_details': validation_results['details'],
                    'data_keys': list(result.data.keys()) if result.data else [],
                    'suggestions_count': len(result.suggestions),
                    'message_length': len(result.message)
                }
                
                self.test_results['test_details'].append(test_result)
                self.test_results['total_tests'] += 1
                
                if validation_results['passed']:
                    self.test_results['passed'] += 1
                    print(f"   ✅ PASSED ({processing_time:.2f}s)")
                else:
                    self.test_results['failed'] += 1
                    print(f"   ❌ FAILED: {validation_results['details']}")
                
                # Show key insights
                if result.data:
                    if 'investment_reality_check' in result.data:
                        check = result.data['investment_reality_check']
                        print(f"   💡 Required yield: {check.get('required_yield_percentage', 'N/A')}%")
                        print(f"   📊 Assessment: {check.get('expectation_assessment', 'N/A')}")
                    elif 'screening_results' in result.data:
                        count = len(result.data['screening_results'])
                        avg_yield = result.data.get('average_yield', 0)
                        print(f"   📈 Found {count} stocks, avg yield: {avg_yield}%")
                    elif 'analysis_results' in result.data:
                        count = len(result.data['analysis_results'])
                        print(f"   🔬 Analyzed {count} stocks with detailed insights")
                
            except Exception as e:
                print(f"   💥 ERROR: {str(e)}")
                self.test_results['total_tests'] += 1
                self.test_results['failed'] += 1
    
    def _validate_response(self, result, expected_type: str, financial_validation: bool, query: str) -> Dict[str, Any]:
        """Validate response structure and content"""
        validation_details = []
        
        # Basic structure validation
        if not result.success:
            return {'passed': False, 'details': 'Response not successful'}
        
        if not result.data:
            return {'passed': False, 'details': 'No data in response'}
        
        # Check expected response type
        if expected_type not in result.data:
            return {'passed': False, 'details': f'Expected {expected_type} not found in response'}
        
        # Validate content based on type
        if expected_type == 'investment_reality_check':
            check = result.data['investment_reality_check']
            required_fields = ['initial_investment', 'target_annual_income', 'required_yield_percentage', 'realistic_scenarios']
            
            for field in required_fields:
                if field not in check:
                    validation_details.append(f'Missing field: {field}')
            
            # Financial validation for investment guidance
            if financial_validation and 'required_yield_percentage' in check:
                required_yield = check['required_yield_percentage']
                if required_yield <= 0 or required_yield > 200:  # Sanity check
                    validation_details.append(f'Unrealistic required yield: {required_yield}%')
        
        elif expected_type == 'screening_results':
            results = result.data['screening_results']
            if len(results) == 0:
                validation_details.append('No screening results returned')
            
            # Check if analysis_results are included
            if 'analysis_results' not in result.data:
                validation_details.append('Enhanced analysis missing from screening')
            
            # Validate first result structure
            if len(results) > 0:
                first_result = results[0]
                required_fields = ['ticker', 'company_name', 'current_price', 'dividend_yield']
                for field in required_fields:
                    if field not in first_result:
                        validation_details.append(f'Missing field in screening result: {field}')
        
        elif expected_type == 'analysis_results':
            analysis = result.data['analysis_results']
            if len(analysis) == 0:
                validation_details.append('No analysis results returned')
            
            # Validate first analysis structure
            if len(analysis) > 0:
                first_ticker = list(analysis.keys())[0]
                first_analysis = analysis[first_ticker]
                required_fields = ['assessment', 'quality_score', 'strengths', 'risks']
                for field in required_fields:
                    if field not in first_analysis:
                        validation_details.append(f'Missing field in analysis: {field}')
        
        # Check suggestions quality
        if len(result.suggestions) < 2:
            validation_details.append('Insufficient suggestions provided')
        
        # Check message quality
        if len(result.message) < 50:
            validation_details.append('Message too short')
        
        return {
            'passed': len(validation_details) == 0,
            'details': '; '.join(validation_details) if validation_details else 'All validations passed'
        }
    
    async def _test_financial_accuracy(self):
        """Test financial calculation accuracy"""
        print(f"\n💰 Testing Financial Accuracy")
        print("-" * 50)
        
        # Known calculation tests
        test_cases = [
            {'investment': 1000, 'monthly_target': 5, 'expected_yield': 6.0},
            {'investment': 5000, 'monthly_target': 20, 'expected_yield': 4.8},
            {'investment': 10000, 'monthly_target': 50, 'expected_yield': 6.0},
        ]
        
        accuracy_results = []
        
        for test in test_cases:
            query = f"I have ${test['investment']} and want to earn ${test['monthly_target']} monthly"
            result = await self.assistant.process_query(query)
            
            if result.success and 'investment_reality_check' in result.data:
                actual_yield = result.data['investment_reality_check']['required_yield_percentage']
                expected_yield = test['expected_yield']
                
                difference = abs(actual_yield - expected_yield)
                accuracy = max(0, 100 - (difference * 10))  # Penalty for each 0.1% difference
                
                accuracy_results.append({
                    'test': test,
                    'expected': expected_yield,
                    'actual': actual_yield,
                    'accuracy': accuracy
                })
                
                print(f"   💵 ${test['investment']} → ${test['monthly_target']}/month")
                print(f"      Expected: {expected_yield}%, Got: {actual_yield}%, Accuracy: {accuracy:.1f}%")
        
        avg_accuracy = sum(r['accuracy'] for r in accuracy_results) / len(accuracy_results)
        self.test_results['financial_accuracy'] = {
            'average_accuracy': avg_accuracy,
            'test_results': accuracy_results
        }
        
        print(f"\n   📊 Overall Financial Accuracy: {avg_accuracy:.1f}%")
    
    async def _test_performance_benchmarks(self):
        """Test performance benchmarks"""
        print(f"\n⚡ Testing Performance Benchmarks")
        print("-" * 50)
        
        # Performance test queries
        queries = [
            'Find dividend stocks with yield above 4%',
            'I have $5000 and want to earn $25 monthly',
            'Analyze AAPL MSFT dividend quality'
        ]
        
        performance_results = []
        
        for query in queries:
            times = []
            for _ in range(3):  # Run 3 times for average
                start_time = time.time()
                result = await self.assistant.process_query(query)
                end_time = time.time()
                if result.success:
                    times.append(end_time - start_time)
            
            if times:
                avg_time = sum(times) / len(times)
                performance_results.append({
                    'query': query,
                    'average_time': avg_time,
                    'times': times
                })
                
                print(f"   🚀 {query[:30]}... → {avg_time:.2f}s avg")
        
        self.test_results['performance_metrics'] = performance_results
    
    async def _generate_comprehensive_report(self):
        """Generate final comprehensive report"""
        print(f"\n📋 COMPREHENSIVE TEST REPORT")
        print("=" * 70)
        
        # Overall statistics
        total = self.test_results['total_tests']
        passed = self.test_results['passed']
        failed = self.test_results['failed']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 Overall Results:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Financial accuracy
        if 'financial_accuracy' in self.test_results:
            fin_accuracy = self.test_results['financial_accuracy']['average_accuracy']
            print(f"   Financial Accuracy: {fin_accuracy:.1f}%")
        
        # Performance summary
        if 'performance_metrics' in self.test_results:
            avg_times = [r['average_time'] for r in self.test_results['performance_metrics']]
            if avg_times:
                overall_avg_time = sum(avg_times) / len(avg_times)
                print(f"   Average Response Time: {overall_avg_time:.2f}s")
        
        # Category breakdown
        print(f"\n📈 Results by Category:")
        categories = {}
        for test in self.test_results['test_details']:
            cat = test['category']
            if cat not in categories:
                categories[cat] = {'passed': 0, 'total': 0}
            categories[cat]['total'] += 1
            if test['validation_passed']:
                categories[cat]['passed'] += 1
        
        for cat, stats in categories.items():
            rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"   {cat}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if success_rate >= 90:
            print("   ✅ System performing excellently")
        elif success_rate >= 75:
            print("   ⚠️  System performing well with minor issues")
        else:
            print("   🚨 System needs significant improvements")
        
        if 'financial_accuracy' in self.test_results:
            fin_accuracy = self.test_results['financial_accuracy']['average_accuracy']
            if fin_accuracy >= 95:
                print("   ✅ Financial calculations are highly accurate")
            elif fin_accuracy >= 85:
                print("   ⚠️  Financial calculations are mostly accurate")
            else:
                print("   🚨 Financial calculations need improvement")
        
        # Save detailed results
        with open('template_validation_report.json', 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: template_validation_report.json")
        print(f"🎯 Validation completed at: {datetime.now().isoformat()}")

async def main():
    validator = TemplateValidator()
    await validator.run_comprehensive_validation()

if __name__ == "__main__":
    asyncio.run(main()) 